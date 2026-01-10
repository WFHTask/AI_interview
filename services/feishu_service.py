"""
Feishu (Lark) Webhook Notification Service

Sends interview results to Feishu group via webhook.
Supports both normal and urgent (S-tier) notifications.
"""
import json
import re
import requests
from typing import Optional
from datetime import datetime

from config.settings import Settings
from models.schemas import FeishuNotification, DecisionTier


# Allowed webhook domains for security (prevent SSRF)
ALLOWED_WEBHOOK_DOMAINS = [
    "open.feishu.cn",
    "open.larksuite.com",  # International version
]


class FeishuServiceError(Exception):
    """Custom exception for Feishu service errors"""
    pass


def is_valid_feishu_webhook(url: str) -> bool:
    """
    Validate that URL is a legitimate Feishu webhook.

    Args:
        url: Webhook URL to validate

    Returns:
        True if URL is valid Feishu webhook
    """
    if not url:
        return False

    # Must be HTTPS
    if not url.startswith("https://"):
        return False

    # Check domain whitelist
    for domain in ALLOWED_WEBHOOK_DOMAINS:
        if url.startswith(f"https://{domain}/"):
            return True

    return False


class FeishuService:
    """
    Feishu Webhook Notification Service

    Sends structured card messages to Feishu groups.
    """

    def __init__(self, webhook_url: str = None):
        """
        Initialize Feishu service

        Args:
            webhook_url: Feishu webhook URL
        """
        self.webhook_url = webhook_url or Settings.FEISHU_WEBHOOK_URL
        self.timeout = 10  # seconds

    def _get_tier_color(self, tier: DecisionTier) -> str:
        """Get color for decision tier"""
        colors = {
            DecisionTier.S: "red",      # Urgent - red
            DecisionTier.A: "green",    # Pass - green
            DecisionTier.B: "orange",   # Backup - orange
            DecisionTier.C: "grey"      # Reject - grey
        }
        return colors.get(tier, "grey")

    def _get_tier_label(self, tier: DecisionTier) -> str:
        """Get label for decision tier"""
        labels = {
            DecisionTier.S: "[S级] 立刻跟进",
            DecisionTier.A: "[A级] 优秀",
            DecisionTier.B: "[B级] 备选",
            DecisionTier.C: "[C级] 淘汰"
        }
        return labels.get(tier, "未知")

    def _build_card_message(self, notification: FeishuNotification) -> dict:
        """
        Build Feishu card message

        Args:
            notification: Notification data

        Returns:
            Card message payload
        """
        tier_color = self._get_tier_color(notification.decision_tier)
        tier_label = self._get_tier_label(notification.decision_tier)

        # Build strengths text
        strengths_text = "\n".join(
            f"• {s}" for s in notification.key_strengths
        ) if notification.key_strengths else "无"

        # Build red flags text
        red_flags_text = "\n".join(
            f"• {r}" for r in notification.red_flags
        ) if notification.red_flags else "无"

        # Build header info content
        header_content = f"**候选人**: {notification.candidate_name}"
        if notification.candidate_email:
            header_content += f"\n**邮箱**: {notification.candidate_email}"
        if notification.job_title:
            header_content += f"\n**应聘岗位**: {notification.job_title}"
        header_content += f"\n**评分**: {notification.total_score}/100\n**评级**: {tier_label}"

        # Card elements
        elements = [
            # Header info
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": header_content
                }
            },
            {"tag": "hr"},
            # Summary
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**评估摘要**\n{notification.summary}"
                }
            },
            {"tag": "hr"},
            # Strengths
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**亮点**\n{strengths_text}"
                }
            },
            # Red flags
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**关注点**\n{red_flags_text}"
                }
            },
            {"tag": "hr"},
            # Session info
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"面试ID: {notification.session_id[:8]}... | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    }
                ]
            }
        ]

        # Add "View Details" button if URL is available
        if notification.detail_url:
            elements.append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "📋 查看完整面试记录"
                        },
                        "type": "primary" if notification.is_urgent else "default",
                        "url": notification.detail_url
                    }
                ]
            })

        # Add chat history (truncated if too long)
        if notification.chat_history_text:
            truncated_history = notification.chat_history_text[:1500]
            if len(notification.chat_history_text) > 1500:
                truncated_history += "\n...(对话过长，已截断)"
            elements.insert(-1, {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**对话记录**\n```\n{truncated_history}\n```"
                }
            })

        # Build card
        card = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"{'[紧急] ' if notification.is_urgent else ''}AI面试结果 - {notification.candidate_name}"
                    },
                    "template": tier_color
                },
                "elements": elements
            }
        }

        return card

    def _build_simple_message(self, notification: FeishuNotification) -> dict:
        """
        Build simple text message (fallback)

        Args:
            notification: Notification data

        Returns:
            Text message payload
        """
        tier_label = self._get_tier_label(notification.decision_tier)
        urgent_prefix = "[紧急] 【S级人才】" if notification.is_urgent else ""

        content = f"""{urgent_prefix}AI面试结果通知

候选人: {notification.candidate_name}
评分: {notification.total_score}/100
评级: {tier_label}

摘要: {notification.summary}

亮点: {', '.join(notification.key_strengths) if notification.key_strengths else '无'}

面试ID: {notification.session_id[:8]}..."""

        return {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }

    def send_notification(
        self,
        notification: FeishuNotification,
        use_card: bool = True
    ) -> bool:
        """
        Send notification to Feishu

        Args:
            notification: Notification data
            use_card: Use card format (True) or simple text (False)

        Returns:
            True if successful
        """
        if not self.webhook_url:
            raise FeishuServiceError("Feishu webhook URL not configured")

        # Security: Validate webhook URL to prevent SSRF
        if not is_valid_feishu_webhook(self.webhook_url):
            raise FeishuServiceError("Invalid Feishu webhook URL. Only open.feishu.cn and open.larksuite.com are allowed.")

        # Build message
        if use_card:
            payload = self._build_card_message(notification)
        else:
            payload = self._build_simple_message(notification)

        # Send request
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            if result.get("code") != 0:
                raise FeishuServiceError(
                    f"Feishu API error: {result.get('msg', 'Unknown error')}"
                )

            return True

        except requests.exceptions.RequestException as e:
            raise FeishuServiceError(f"Failed to send notification: {e}")

    def send_s_tier_alert(
        self,
        notification: FeishuNotification,
        additional_message: str = ""
    ) -> bool:
        """
        Send urgent S-tier alert

        Args:
            notification: Notification data
            additional_message: Extra message to include

        Returns:
            True if successful
        """
        if notification.decision_tier != DecisionTier.S:
            return self.send_notification(notification)

        # For S-tier, send card + follow-up text
        card_sent = self.send_notification(notification, use_card=True)

        # Send additional alert text
        if additional_message and card_sent:
            alert_payload = {
                "msg_type": "text",
                "content": {
                    "text": f"[紧急] S级人才预警！\n\n{additional_message}\n\n请立即跟进！"
                }
            }

            try:
                response = requests.post(
                    self.webhook_url,
                    json=alert_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout
                )
                # Log but don't fail if additional message fails
                if response.status_code != 200:
                    import logging
                    logging.warning(f"Failed to send S-tier additional alert: {response.status_code}")
            except Exception as e:
                import logging
                logging.warning(f"Failed to send S-tier additional alert: {e}")

        return card_sent

    def test_connection(self) -> bool:
        """
        Test webhook connection

        Returns:
            True if connection successful
        """
        if not self.webhook_url:
            return False

        test_payload = {
            "msg_type": "text",
            "content": {
                "text": "[测试] AI面试系统 - 连接测试成功！"
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            return response.status_code == 200
        except:
            return False


# Singleton instance
feishu_service = FeishuService()


def send_interview_result(
    notification: FeishuNotification,
    webhook_url: str = None
) -> bool:
    """
    Convenience function to send interview result notification

    Args:
        notification: Notification data
        webhook_url: Optional custom webhook URL

    Returns:
        True if successful
    """
    service = FeishuService(webhook_url) if webhook_url else feishu_service

    if notification.is_urgent:
        return service.send_s_tier_alert(notification)
    else:
        return service.send_notification(notification)

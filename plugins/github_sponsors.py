"""GitHub Sponsors 赚钱模块 — MVP核心赚钱渠道"""
import time
from plugins.base import RevenuePlugin, RevenueReport
from utils.github_api import GitHubAPI


class GitHubSponsorsPlugin(RevenuePlugin):
    """通过 GitHub Sponsors 赚取开源赞助"""

    def check_credentials(self) -> bool:
        """验证 GitHub Token"""
        try:
            api = GitHubAPI(self.config["github_token"])
            user = api.get_user()
            return user is not None and "login" in user
        except Exception:
            return False

    def get_revenue_report(self) -> RevenueReport:
        """获取赞助收入"""
        try:
            api = GitHubAPI(self.config["github_token"])
            sponsors = api.get_sponsors()

            total = 0.0
            sponsor_count = 0
            for sponsor in sponsors:
                if isinstance(sponsor, dict):
                    sponsor_count += 1
                    tier = sponsor.get("tier", {}) if isinstance(sponsor.get("tier"), dict) else {}
                    amount = tier.get("monthly_price_in_dollars", 0)
                    total += amount

            return RevenueReport(
                platform="github_sponsors",
                period=time.strftime("%Y-%m"),
                gross_income=total,
                net_income=total,
                details={
                    "sponsor_count": sponsor_count,
                    "estimated_monthly": total,
                },
            )
        except Exception as e:
            return RevenueReport(
                platform="github_sponsors",
                period=time.strftime("%Y-%m"),
                gross_income=0,
                net_income=0,
                details={"error": str(e)},
            )

    def do_work(self) -> dict:
        """执行一轮GitHub运营工作"""
        actions = []
        try:
            api = GitHubAPI(self.config["github_token"])
            owner = self.config["repo_owner"]
            repo = self.config["repo_name"]

            issues = api.get_issues(owner, repo, labels="agent-input")
            actions.append(f"读取到 {len(issues)} 个待处理Issue")

            for issue in issues[:5]:
                issue_number = issue.get("number")
                title = issue.get("title", "")
                actions.append(f"处理Issue #{issue_number}: {title}")
                api.comment_issue(
                    owner, repo, issue_number,
                    f"🐙 收到！已加入本次进化计划。\n\n"
                    f"当前状态：正在分析中...\n"
                    f"预计下次醒来时处理。"
                )

            sponsors = api.get_sponsors()
            actions.append(f"当前赞助者: {len(sponsors)} 人")

            if len(issues) == 0:
                api.create_issue(
                    owner, repo,
                    title="🤖 Agent自驱任务：持续改进",
                    body="本轮没有社区需求，Agent自主选择改进方向。\n\n"
                         "改进目标：\n"
                         "1. 优化代码质量\n"
                         "2. 完善文档\n"
                         "3. 探索新功能\n",
                    labels=["agent-self"],
                )
                actions.append("创建自驱改进Issue")

            return {
                "action": "GitHub运营",
                "result": "; ".join(actions),
                "revenue_impact": 0.0,
                "cost": 0.0,
            }
        except Exception as e:
            return {
                "action": "GitHub运营",
                "result": f"出错: {e}",
                "revenue_impact": 0.0,
                "cost": 0.0,
            }

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "repo": f"{self.config.get('repo_owner', '?')}/{self.config.get('repo_name', '?')}",
        }

    def _generate_work_plan(self, issues: list, repo_status: str) -> list:
        """生成工作计划（供进化引擎调用）"""
        plan = []
        if issues:
            for issue in issues:
                plan.append({
                    "type": "fix_issue",
                    "issue_number": issue.get("number"),
                    "title": issue.get("title"),
                    "body": issue.get("body", "")[:200],
                })
        else:
            plan.append({
                "type": "self_improve",
                "description": "Agent自主选择改进方向",
            })
        return plan

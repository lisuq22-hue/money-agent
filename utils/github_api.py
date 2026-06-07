"""GitHub API 封装 — REST API 调用"""
import httpx


class GitHubAPI:
    """GitHub REST API 客户端"""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "MoneyAgent/0.1.0",
        }

    def _request(self, method: str, path: str, **kwargs) -> dict | list | None:
        """发送API请求"""
        url = f"{self.BASE_URL}{path}"
        try:
            with httpx.Client(timeout=30) as client:
                response = client.request(
                    method, url, headers=self.headers, **kwargs
                )
                if response.status_code == 401:
                    raise PermissionError("GitHub Token 无效或已过期")
                if response.status_code == 403 and "rate limit" in response.text.lower():
                    raise RuntimeError("GitHub API 限流，需要降频")
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                if response.text:
                    return response.json()
                return None
        except httpx.ConnectError:
            raise ConnectionError("无法连接 GitHub API，请检查网络/代理")

    def get_user(self) -> dict:
        """获取当前用户信息（验证Token）"""
        return self._request("GET", "/user")

    def get_repo(self, owner: str, repo: str) -> dict:
        """获取仓库信息"""
        return self._request("GET", f"/repos/{owner}/{repo}")

    def create_repo(self, name: str, description: str = "", private: bool = False) -> dict:
        """创建仓库"""
        return self._request("POST", "/user/repos", json={
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True,
        })

    def get_issues(self, owner: str, repo: str, labels: str = "", state: str = "open") -> list:
        """获取Issues"""
        params = {"state": state, "per_page": 30}
        if labels:
            params["labels"] = labels
        result = self._request("GET", f"/repos/{owner}/{repo}/issues", params=params)
        return result or []

    def create_issue(self, owner: str, repo: str, title: str, body: str,
                     labels: list = None) -> dict:
        """创建Issue"""
        return self._request("POST", f"/repos/{owner}/{repo}/issues", json={
            "title": title,
            "body": body,
            "labels": labels or [],
        })

    def comment_issue(self, owner: str, repo: str, issue_number: int, body: str) -> dict:
        """回复Issue"""
        return self._request("POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            json={"body": body})

    def get_sponsors(self) -> list:
        """获取赞助者列表"""
        result = self._request("GET", "/user/sponsors")
        return result or []

    def check_sponsors_enabled(self, owner: str) -> bool:
        """检查是否开启了Sponsors"""
        result = self._request("GET", f"/users/{owner}")
        if result and isinstance(result, dict):
            return True
        return False

"""模拟银行业务工具

提供模拟的银行账户查询、转账等操作，用于演示和测试。
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class AccountQueryInput(BaseModel):
    """账户查询输入"""

    account_number: str = Field(..., description="账户号码")


class AccountQueryTool(BaseTool):
    """模拟账户查询工具

    查询指定账户的基本信息（余额、户名、账户状态）。
    注意：这是模拟数据，不连接真实银行系统。
    """

    name: str = "account_query"
    description: str = (
        "查询银行账户信息，包括余额、户名、账户状态。"
        "输入账户号码，返回账户基本信息。注意：这是模拟数据。"
    )
    args_schema: type[BaseModel] = AccountQueryInput

    def _run(self, account_number: str) -> str:
        """执行账户查询（模拟）"""
        # 模拟数据
        mock_accounts = {
            "6222021234567890": {
                "户名": "张三",
                "余额": "¥ 25,680.50",
                "账户状态": "正常",
                "开户行": "北京分行朝阳支行",
                "账户类型": "个人储蓄账户",
            },
            "6222021234567891": {
                "户名": "李四",
                "余额": "¥ 128,350.00",
                "账户状态": "正常",
                "开户行": "上海分行浦东支行",
                "账户类型": "个人储蓄账户",
            },
            "6222021234567892": {
                "户名": "王五",
                "余额": "¥ 3,250.75",
                "账户状态": "冻结",
                "开户行": "广州分行天河支行",
                "账户类型": "个人储蓄账户",
                "备注": "因挂失申请已冻结",
            },
        }

        account = mock_accounts.get(account_number)
        if not account:
            return f"[模拟数据] 未找到账户 {account_number} 的信息。请确认账户号码是否正确。"

        info = "\n".join(f"{k}: {v}" for k, v in account.items())
        return f"[模拟数据] 账户信息查询结果：\n{info}"


class TransferInput(BaseModel):
    """转账输入"""

    from_account: str = Field(..., description="转出账户号码")
    to_account: str = Field(..., description="转入账户号码")
    amount: float = Field(..., description="转账金额")
    transfer_type: str = Field("internal", description="转账类型: internal（行内）/ external（跨行）")


class TransferTool(BaseTool):
    """模拟转账工具

    执行账户间转账操作（模拟）。
    注意：这是模拟数据，不连接真实银行系统。
    """

    name: str = "transfer"
    description: str = (
        "执行银行转账操作。输入转出账户、转入账户、金额和转账类型。"
        "注意：这是模拟数据，不会产生真实的资金变动。"
    )
    args_schema: type[BaseModel] = TransferInput

    def _run(self, from_account: str, to_account: str, amount: float, transfer_type: str = "internal") -> str:
        """执行转账（模拟）"""
        if amount <= 0:
            return "[模拟数据] 转账失败：金额必须大于零。"

        if amount > 500000:
            return "[模拟数据] 转账失败：单笔转账金额超过限额（¥500,000）。"

        # 模拟手续费
        fee = 0.0 if transfer_type == "internal" else amount * 0.001  # 跨行 0.1%
        fee = max(fee, 2.0) if transfer_type == "external" else 0.0  # 跨行最低 2 元

        total = amount + fee

        return (
            f"[模拟数据] 转账预处理完成：\n"
            f"- 转出账户: {from_account}\n"
            f"- 转入账户: {to_account}\n"
            f"- 转账金额: ¥ {amount:,.2f}\n"
            f"- 转账类型: {'行内转账' if transfer_type == 'internal' else '跨行转账'}\n"
            f"- 手续费: ¥ {fee:,.2f}\n"
            f"- 扣款总额: ¥ {total:,.2f}\n"
            f"⚠️ 这是模拟转账，不会产生真实资金变动。"
        )


class FreezeAccountInput(BaseModel):
    """冻结账户输入"""

    account_number: str = Field(..., description="要冻结的账户号码")
    reason: str = Field("客户申请挂失", description="冻结原因")


class FreezeAccountTool(BaseTool):
    """模拟冻结账户工具

    冻结指定账户（模拟）。
    注意：这是模拟数据，不连接真实银行系统。
    """

    name: str = "freeze_account"
    description: str = (
        "冻结指定银行账户。输入账户号码和冻结原因。"
        "注意：这是模拟数据，不会产生真实的账户状态变更。"
    )
    args_schema: type[BaseModel] = FreezeAccountInput

    def _run(self, account_number: str, reason: str = "客户申请挂失") -> str:
        """执行账户冻结（模拟）"""
        return (
            f"[模拟数据] 账户冻结操作已完成：\n"
            f"- 账户号码: {account_number}\n"
            f"- 冻结原因: {reason}\n"
            f"- 操作时间: 模拟时间\n"
            f"- 操作状态: 成功\n"
            f"⚠️ 这是模拟操作，不会产生真实的账户状态变更。"
        )


# 创建工具实例
account_query_tool = AccountQueryTool()
transfer_tool = TransferTool()
freeze_account_tool = FreezeAccountTool()

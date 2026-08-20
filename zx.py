import discord
from discord.ext import commands
from discord import ui
import traceback


# =========================================================
# 設定
# =========================================================

# ⚠️ 請放入重新產生的新 Bot Token
TOKEN = "MTUzODA3NDk1OTEzMjM2MDgxNg.GX7AAY.h2J-ITuknNj3MujObISIO0-ltLscjsxJA_grzQ"

# 固定考試頻道
TICKET_CHANNEL_ID = 1525710386253529289

# 工作人員身分組
# 沒有就保持 0
STAFF_ROLE_ID = 0

# =========================================================
# Discord 單檔安全上限
#
# 注意：
# 這裡不是用來突破 Discord 限制。
# 只是提前避免送出一定會 413 的檔案。
#
# 如果你的 Bot 所在帳號實際限制不同，
# 可以再往下調整。
# =========================================================

SAFE_UPLOAD_SIZE = 9 * 1024 * 1024


# =========================================================
# Intents
# =========================================================

intents = discord.Intents.default()

intents.guilds = True
intents.members = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# 暫存表單
# =========================================================

user_forms = {}


def get_form(user_id: int):

    if user_id not in user_forms:

        user_forms[user_id] = {

            "roblox_id": "",

            "device": "",

            "attachments": [],

            "highlight_link": ""
        }

    return user_forms[user_id]


# =========================================================
# Roblox ID Modal
# =========================================================

class RobloxIDModal(ui.Modal):

    def __init__(
        self,
        user_id: int
    ):

        super().__init__(
            title="填入 Roblox 使用者",
            timeout=300
        )

        self.user_id = user_id

        self.roblox_id = ui.TextInput(

            label="請輸入你的遊戲 Roblox 使用者ID",

            placeholder="例如：123456789",

            required=True,

            min_length=1,

            max_length=50
        )

        self.add_item(
            self.roblox_id
        )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        try:

            if interaction.user.id != self.user_id:

                await interaction.response.send_message(
                    "❌ 這個表單不是你的。",
                    ephemeral=True
                )

                return

            data = get_form(
                self.user_id
            )

            data["roblox_id"] = (
                self.roblox_id.value.strip()
            )

            print(
                f"✅ {interaction.user} "
                f"填入 Roblox ID："
                f"{data['roblox_id']}"
            )

            await interaction.response.send_message(

                view=ExamFormView(
                    self.user_id
                ),

                ephemeral=True
            )

        except Exception:

            print(
                "❌ RobloxIDModal 發生錯誤"
            )

            traceback.print_exc()

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "❌ 儲存 Roblox ID 時發生錯誤。",
                    ephemeral=True
                )


# =========================================================
# Roblox Button
# =========================================================

class RobloxButton(ui.Button):

    def __init__(
        self,
        user_id: int
    ):

        super().__init__(

            label="填入 Roblox 使用者",

            style=discord.ButtonStyle.secondary
        )

        self.user_id = user_id

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "❌ 這個表單不是你的。",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(

            RobloxIDModal(
                self.user_id
            )
        )


# =========================================================
# 裝置選擇
# =========================================================

class DeviceSelect(ui.Select):

    def __init__(
        self,
        user_id: int
    ):

        self.user_id = user_id

        options = [

            discord.SelectOption(
                label="手機",
                value="手機",
                description="使用手機遊玩"
            ),

            discord.SelectOption(
                label="電腦",
                value="電腦",
                description="使用電腦遊玩"
            ),

            discord.SelectOption(
                label="平板",
                value="平板",
                description="使用平板遊玩"
            )
        ]

        super().__init__(

            placeholder="選擇裝置",

            min_values=1,

            max_values=1,

            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        try:

            if interaction.user.id != self.user_id:

                await interaction.response.send_message(
                    "❌ 這個表單不是你的。",
                    ephemeral=True
                )

                return

            data = get_form(
                self.user_id
            )

            data["device"] = self.values[0]

            print(
                f"✅ {interaction.user} "
                f"選擇裝置："
                f"{data['device']}"
            )

            await interaction.response.edit_message(

                view=ExamFormView(
                    self.user_id
                )
            )

        except Exception:

            print(
                "❌ DeviceSelect 發生錯誤"
            )

            traceback.print_exc()


# =========================================================
# 上傳圖片／影片
# =========================================================

class UploadModal(ui.Modal):

    def __init__(
        self,
        user_id: int
    ):

        super().__init__(

            title="上傳圖片／影片",

            timeout=300
        )

        self.user_id = user_id

        self.files = ui.FileUpload(

            required=True,

            min_values=1,

            max_values=10
        )

        self.add_item(

            ui.Label(

                text="上傳考試相關圖片或影片",

                description="最多可以上傳 10 個檔案",

                component=self.files
            )
        )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        try:

            if interaction.user.id != self.user_id:

                await interaction.response.send_message(
                    "❌ 這個表單不是你的。",
                    ephemeral=True
                )

                return

            data = get_form(
                self.user_id
            )

            data["attachments"] = list(
                self.files.values
            )

            print(
                "========================================"
            )

            print(
                f"📥 {interaction.user} "
                f"上傳 "
                f"{len(data['attachments'])} 個檔案"
            )

            for attachment in data["attachments"]:

                print(
                    f"   📎 {attachment.filename}"
                )

                print(
                    f"   📦 大小："
                    f"{attachment.size / 1024 / 1024:.2f} MB"
                )

            print(
                "========================================"
            )

            await interaction.response.send_message(

                view=ExamFormView(
                    self.user_id
                ),

                ephemeral=True
            )

        except Exception:

            print(
                "❌ UploadModal 發生錯誤"
            )

            traceback.print_exc()

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "❌ 上傳圖片／影片時發生錯誤。",
                    ephemeral=True
                )


# =========================================================
# 上傳按鈕
# =========================================================

class UploadButton(ui.Button):

    def __init__(
        self,
        user_id: int
    ):

        super().__init__(

            label="上傳圖片／影片",

            style=discord.ButtonStyle.secondary
        )

        self.user_id = user_id

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "❌ 這個表單不是你的。",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(

            UploadModal(
                self.user_id
            )
        )


# =========================================================
# 精華影片連結
# =========================================================

class HighlightModal(ui.Modal):

    def __init__(
        self,
        user_id: int
    ):

        super().__init__(

            title="精華影片連結",

            timeout=300
        )

        self.user_id = user_id

        self.link = ui.TextInput(

            label="請放入你的精華影片連結",

            placeholder="https://...",

            required=True,

            max_length=1000
        )

        self.add_item(
            self.link
        )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        try:

            if interaction.user.id != self.user_id:

                await interaction.response.send_message(
                    "❌ 這個表單不是你的。",
                    ephemeral=True
                )

                return

            data = get_form(
                self.user_id
            )

            data["highlight_link"] = (
                self.link.value.strip()
            )

            print(
                f"✅ {interaction.user} "
                "已填入精華影片連結"
            )

            await interaction.response.send_message(

                view=ExamFormView(
                    self.user_id
                ),

                ephemeral=True
            )

        except Exception:

            print(
                "❌ HighlightModal 發生錯誤"
            )

            traceback.print_exc()

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "❌ 儲存精華影片連結時發生錯誤。",
                    ephemeral=True
                )


# =========================================================
# 精華影片按鈕
# =========================================================

class HighlightButton(ui.Button):

    def __init__(
        self,
        user_id: int
    ):

        super().__init__(

            label="放入精華影片連結",

            style=discord.ButtonStyle.secondary
        )

        self.user_id = user_id

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "❌ 這個表單不是你的。",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(

            HighlightModal(
                self.user_id
            )
        )


# =========================================================
# 取消
# =========================================================

class CancelButton(ui.Button):

    def __init__(
        self,
        user_id: int
    ):

        super().__init__(

            label="取消",

            style=discord.ButtonStyle.danger
        )

        self.user_id = user_id

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "❌ 這個表單不是你的。",
                ephemeral=True
            )

            return

        user_forms.pop(
            self.user_id,
            None
        )

        await interaction.response.edit_message(

            view=CancelledView()
        )


# =========================================================
# 確認
# =========================================================

class ConfirmButton(ui.Button):

    def __init__(
        self,
        user_id: int
    ):

        super().__init__(

            label="確認",

            style=discord.ButtonStyle.success
        )

        self.user_id = user_id

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        try:

            if interaction.user.id != self.user_id:

                await interaction.response.send_message(
                    "❌ 這個表單不是你的。",
                    ephemeral=True
                )

                return

            data = get_form(
                self.user_id
            )

            # =================================================
            # 檢查資料
            # =================================================

            if not data["roblox_id"]:

                await interaction.response.send_message(
                    "⚠️ 請先填入 Roblox 使用者 ID。",
                    ephemeral=True
                )

                return

            if not data["device"]:

                await interaction.response.send_message(
                    "⚠️ 請先選擇裝置。",
                    ephemeral=True
                )

                return

            if not data["attachments"]:

                await interaction.response.send_message(
                    "⚠️ 請先上傳圖片或影片。",
                    ephemeral=True
                )

                return

            if not data["highlight_link"]:

                await interaction.response.send_message(
                    "⚠️ 請先放入精華影片連結。",
                    ephemeral=True
                )

                return

            guild = interaction.guild

            if guild is None:

                await interaction.response.send_message(
                    "❌ 找不到伺服器。",
                    ephemeral=True
                )

                return

            # =================================================
            # 回應
            # =================================================

            await interaction.response.defer(
                ephemeral=True
            )

            # =================================================
            # 頻道名稱
            # =================================================

            username = (

                interaction.user.name

                .lower()

                .replace(
                    " ",
                    "-"
                )
            )

            channel_name = (
                f"考試-{username}"
            )[:100]

            # =================================================
            # 權限
            # =================================================

            overwrites = {

                guild.default_role:

                    discord.PermissionOverwrite(

                        view_channel=False
                    ),

                interaction.user:

                    discord.PermissionOverwrite(

                        view_channel=True,

                        send_messages=True,

                        read_message_history=True,

                        attach_files=True
                    )
            }

            if STAFF_ROLE_ID:

                staff_role = guild.get_role(
                    STAFF_ROLE_ID
                )

                if staff_role:

                    overwrites[staff_role] = (

                        discord.PermissionOverwrite(

                            view_channel=True,

                            send_messages=True,

                            read_message_history=True,

                            attach_files=True
                        )
                    )

            # =================================================
            # 建立私人頻道
            # =================================================

            print(
                f"📁 建立私人頻道："
                f"{channel_name}"
            )

            ticket_channel = (

                await guild.create_text_channel(

                    name=channel_name,

                    overwrites=overwrites,

                    reason="考試申請私人頻道"
                )
            )

            print(
                f"✅ 頻道建立成功："
                f"{ticket_channel.id}"
            )

            # =================================================
            # 先發送申請資料
            # =================================================

            try:

                await ticket_channel.send(

                    view=TicketInfoView(

                        interaction.user,

                        data
                    )
                )

                print(
                    "✅ 申請資料已發送"
                )

            except Exception:

                print(
                    "❌ 申請資料發送失敗"
                )

                traceback.print_exc()

            # =================================================
            # 檔案處理
            # =================================================

            normal_files = []

            large_files = []

            print(
                "========================================"
            )

            print(
                "📦 開始處理所有附件"
            )

            print(
                "========================================"
            )

            for attachment in data["attachments"]:

                try:

                    size_mb = (
                        attachment.size
                        /
                        1024
                        /
                        1024
                    )

                    print(
                        f"📎 {attachment.filename}"
                    )

                    print(
                        f"   大小："
                        f"{size_mb:.2f} MB"
                    )

                    # =================================================
                    # 超過安全大小
                    # =================================================

                    if attachment.size > SAFE_UPLOAD_SIZE:

                        print(
                            "   ⚠️ 檔案過大"
                        )

                        large_files.append(
                            attachment
                        )

                        continue

                    # =================================================
                    # 正常檔案
                    # =================================================

                    print(
                        "   📥 正在下載附件..."
                    )

                    file = await attachment.to_file()

                    normal_files.append(
                        (
                            attachment,
                            file
                        )
                    )

                    print(
                        "   ✅ 檔案準備完成"
                    )

                except Exception:

                    print(
                        f"❌ 處理附件失敗："
                        f"{attachment.filename}"
                    )

                    traceback.print_exc()

                    large_files.append(
                        attachment
                    )

            # =================================================
            # 逐個上傳正常檔案
            # =================================================

            uploaded = []

            for attachment, file in normal_files:

                try:

                    print(
                        f"📤 正在上傳："
                        f"{attachment.filename}"
                    )

                    message = (

                        await ticket_channel.send(

                            file=file
                        )
                    )

                    if message.attachments:

                        uploaded_attachment = (
                            message.attachments[0]
                        )

                        uploaded.append(
                            uploaded_attachment
                        )

                    print(
                        f"✅ 上傳成功："
                        f"{attachment.filename}"
                    )

                except discord.HTTPException as e:

                    print(
                        f"❌ 檔案發送失敗："
                        f"{attachment.filename}"
                    )

                    print(
                        f"   HTTP 狀態："
                        f"{getattr(e, 'status', '未知')}"
                    )

                    print(
                        f"   Discord 錯誤："
                        f"{e}"
                    )

                    # =========================================
                    # 即使 413 也不影響其他檔案
                    # =========================================

                    large_files.append(
                        attachment
                    )

                except Exception:

                    print(
                        f"❌ 發送檔案時發生錯誤："
                        f"{attachment.filename}"
                    )

                    traceback.print_exc()

                    large_files.append(
                        attachment
                    )

            # =================================================
            # 建立 MediaGallery
            # =================================================

            if uploaded:

                print(
                    f"🖼️ 建立 MediaGallery："
                    f"{len(uploaded)} 個"
                )

                try:

                    for start in range(
                        0,
                        len(uploaded),
                        10
                    ):

                        current = uploaded[
                            start:start + 10
                        ]

                        items = []

                        for attachment in current:

                            items.append(

                                discord.MediaGalleryItem(

                                    media=attachment.url
                                )
                            )

                        gallery = ui.MediaGallery(
                            *items
                        )

                        container = ui.Container(

                            ui.TextDisplay(
                                "# 🖼️ 上傳的圖片／影片"
                            ),

                            ui.Separator(),

                            gallery,

                            ui.Separator(),

                            ui.TextDisplay(
                                "以上為使用者上傳的檔案。"
                            )
                        )

                        view = ui.LayoutView()

                        view.add_item(
                            container
                        )

                        await ticket_channel.send(
                            view=view
                        )

                        print(
                            "✅ MediaGallery 發送成功"
                        )

                except Exception:

                    print(
                        "❌ MediaGallery 發送失敗"
                    )

                    traceback.print_exc()

            # =================================================
            # 超大檔案
            # =================================================

            if large_files:

                print(
                    "========================================"
                )

                print(
                    f"⚠️ 有 {len(large_files)} 個檔案超過 Discord Bot 附件限制"
                )

                print(
                    "========================================"
                )

                container = ui.Container(

                    ui.TextDisplay(
                        "# ⚠️ 大型檔案"
                    ),

                    ui.Separator(),

                    ui.TextDisplay(
                        "以下檔案超過 Discord Bot 可重新上傳的大小限制。\n"
                        "原始附件連結仍然保留，可以點擊開啟。"
                    )
                )

                for attachment in large_files:

                    size_mb = (

                        attachment.size
                        /
                        1024
                        /
                        1024
                    )

                    container.add_item(

                        ui.TextDisplay(

                            f"📎 **{attachment.filename}**\n"
                            f"大小：`{size_mb:.2f} MB`\n"
                            f"原始附件：{attachment.url}"
                        )
                    )

                    container.add_item(
                        ui.Separator()
                    )

                view = ui.LayoutView()

                view.add_item(
                    container
                )

                try:

                    await ticket_channel.send(
                        view=view
                    )

                    print(
                        "✅ 大型檔案資訊已發送"
                    )

                except Exception:

                    print(
                        "❌ 大型檔案資訊發送失敗"
                    )

                    traceback.print_exc()

            # =================================================
            # 完全沒有成功
            # =================================================

            if not uploaded and not large_files:

                await ticket_channel.send(

                    view=SimpleErrorView(

                        "⚠️ 沒有任何檔案成功處理。"
                    )
                )

            # =================================================
            # 清除暫存
            # =================================================

            user_forms.pop(
                self.user_id,
                None
            )

            # =================================================
            # 完成
            # =================================================

            await interaction.edit_original_response(

                view=FinishedView(
                    ticket_channel
                )
            )

            print(
                "========================================"
            )

            print(
                "✅ 考試申請完成"
            )

            print(
                "========================================"
            )

        except discord.Forbidden:

            print(
                "❌ Bot 權限不足"
            )

            traceback.print_exc()

            try:

                await interaction.edit_original_response(

                    content=(

                        "❌ Bot 權限不足。\n"

                        "請確認 Bot 有建立頻道、"

                        "查看頻道及發送訊息的權限。"
                    )
                )

            except Exception:

                pass

        except Exception:

            print(
                "❌ ConfirmButton 發生錯誤"
            )

            traceback.print_exc()

            try:

                await interaction.edit_original_response(

                    content=(

                        "❌ 建立私人頻道時發生錯誤。\n"

                        "請查看 Bot 主控台。"
                    )
                )

            except Exception:

                pass


# =========================================================
# 開單按鈕
# =========================================================

class OpenTicketButton(ui.Button):

    def __init__(self):

        super().__init__(

            label="開單",

            style=discord.ButtonStyle.primary,

            custom_id="exam_open_ticket"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        get_form(
            interaction.user.id
        )

        await interaction.response.send_message(

            view=ExamFormView(
                interaction.user.id
            ),

            ephemeral=True
        )


# =========================================================
# 固定頻道面板
# =========================================================

class MainPanel(ui.LayoutView):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        container = ui.Container(

            ui.TextDisplay(

                "# 考試\n"
                "請點擊下面的開單按鈕開始考試。"
            ),

            ui.Separator(),

            ui.Section(

                ui.TextDisplay(
                    "開始考試申請"
                ),

                accessory=OpenTicketButton()
            )
        )

        self.add_item(
            container
        )


# =========================================================
# 個人表格
# =========================================================

class ExamFormView(ui.LayoutView):

    def __init__(
        self,
        user_id: int
    ):

        super().__init__(
            timeout=600
        )

        data = get_form(
            user_id
        )

        # =================================================
        # 狀態
        # =================================================

        if data["roblox_id"]:

            roblox_status = (
                f"已填入：`{data['roblox_id']}`"
            )

        else:

            roblox_status = "尚未填入"

        if data["device"]:

            device_status = (
                f"已選擇：`{data['device']}`"
            )

        else:

            device_status = "尚未選擇"

        if data["attachments"]:

            file_status = (

                f"已上傳 "
                f"{len(data['attachments'])} 個檔案"
            )

        else:

            file_status = "尚未上傳"

        if data["highlight_link"]:

            link_status = "已填入"

        else:

            link_status = "尚未填入"

        # =================================================
        # Container
        # =================================================

        container = ui.Container(

            ui.TextDisplay(

                "# 填入表格\n"
                "請完成以下資料。"
            ),

            ui.Separator(),

            ui.TextDisplay(

                f"**Roblox 使用者**\n"
                f"{roblox_status}"
            ),

            ui.Section(

                ui.TextDisplay(
                    "填入你的 Roblox 使用者 ID"
                ),

                accessory=RobloxButton(
                    user_id
                )
            ),

            ui.Separator(),

            ui.TextDisplay(

                f"**選擇裝置**\n"
                f"{device_status}"
            ),

            ui.ActionRow(

                DeviceSelect(
                    user_id
                )
            ),

            ui.Separator(),

            ui.TextDisplay(

                f"**上傳圖片／影片**\n"
                f"{file_status}"
            ),

            ui.Section(

                ui.TextDisplay(
                    "上傳考試相關圖片或影片"
                ),

                accessory=UploadButton(
                    user_id
                )
            ),

            ui.Separator(),

            ui.TextDisplay(

                f"**精華影片連結**\n"
                f"{link_status}"
            ),

            ui.Section(

                ui.TextDisplay(
                    "放入你的精華影片連結"
                ),

                accessory=HighlightButton(
                    user_id
                )
            ),

            ui.Separator(),

            ui.ActionRow(

                ConfirmButton(
                    user_id
                ),

                CancelButton(
                    user_id
                )
            )
        )

        self.add_item(
            container
        )


# =========================================================
# 申請資料
# =========================================================

class TicketInfoView(ui.LayoutView):

    def __init__(
        self,
        user: discord.Member,
        data: dict
    ):

        super().__init__(
            timeout=None
        )

        container = ui.Container(

            ui.TextDisplay(
                "# 📋 考試申請"
            ),

            ui.TextDisplay(

                f"**申請人**\n"
                f"{user.mention}"
            ),

            ui.Separator(),

            ui.TextDisplay(

                f"**Roblox 使用者 ID**\n"
                f"`{data['roblox_id']}`"
            ),

            ui.TextDisplay(

                f"**使用裝置**\n"
                f"`{data['device']}`"
            ),

            ui.Separator(),

            ui.TextDisplay(
                "**精華影片連結**"
            ),

            ui.TextDisplay(
                data["highlight_link"]
            ),

            ui.Separator(),

            ui.TextDisplay(
                "請工作人員確認以上資料。"
            )
        )

        self.add_item(
            container
        )


# =========================================================
# 完成
# =========================================================

class FinishedView(ui.LayoutView):

    def __init__(
        self,
        channel: discord.TextChannel
    ):

        super().__init__(
            timeout=120
        )

        container = ui.Container(

            ui.TextDisplay(

                "# ✅ 開單成功\n\n"

                f"你的私人考試頻道："
                f"{channel.mention}\n\n"

                "請前往該頻道等待工作人員處理。"
            )
        )

        self.add_item(
            container
        )


# =========================================================
# 取消
# =========================================================

class CancelledView(ui.LayoutView):

    def __init__(self):

        super().__init__(
            timeout=60
        )

        container = ui.Container(

            ui.TextDisplay(

                "# ❌ 已取消\n\n"
                "這次考試申請已取消。"
            )
        )

        self.add_item(
            container
        )


# =========================================================
# 錯誤
# =========================================================

class SimpleErrorView(ui.LayoutView):

    def __init__(
        self,
        message: str
    ):

        super().__init__(
            timeout=None
        )

        container = ui.Container(

            ui.TextDisplay(
                message
            )
        )

        self.add_item(
            container
        )


# =========================================================
# 持久化按鈕
# =========================================================

@bot.event
async def setup_hook():

    try:

        bot.add_view(
            MainPanel()
        )

        print(
            "✅ 固定開單按鈕已註冊"
        )

    except Exception:

        traceback.print_exc()


# =========================================================
# Bot Ready
# =========================================================

@bot.event
async def on_ready():

    print()

    print(
        "=========================================="
    )

    print(
        f"✅ Bot：{bot.user}"
    )

    print(
        f"🆔 Bot ID：{bot.user.id}"
    )

    print(
        "=========================================="
    )

    try:

        channel = bot.get_channel(
            TICKET_CHANNEL_ID
        )

        if channel is None:

            channel = await bot.fetch_channel(
                TICKET_CHANNEL_ID
            )

        found_panel = False

        async for message in channel.history(
            limit=50
        ):

            if message.author.id != bot.user.id:

                continue

            if message.components:

                found_panel = True

                print(
                    "ℹ️ 固定頻道已存在考試面板。"
                )

                break

        if not found_panel:

            await channel.send(

                view=MainPanel()
            )

            print(
                "✅ 已建立考試 Components V2 面板。"
            )

    except discord.Forbidden:

        print(
            "❌ Bot 沒有查看或發送訊息的權限。"
        )

    except discord.NotFound:

        print(
            f"❌ 找不到頻道："
            f"{TICKET_CHANNEL_ID}"
        )

    except Exception:

        traceback.print_exc()


# =========================================================
# 全域錯誤
# =========================================================

@bot.event
async def on_error(
    event,
    *args,
    **kwargs
):

    print(
        f"❌ Discord Event Error：{event}"
    )

    traceback.print_exc()


# =========================================================
# 啟動
# =========================================================

if __name__ == "__main__":

    if (

        not TOKEN.strip()

        or TOKEN == "請填入新的 BOT TOKEN"

    ):

        print(
            "❌ 請先把新的 Bot Token 填入 TOKEN。"
        )

    else:

        try:

            bot.run(
                TOKEN
            )

        except discord.LoginFailure:

            print(
                "❌ Bot Token 無效。"
            )

        except Exception:

            traceback.print_exc()
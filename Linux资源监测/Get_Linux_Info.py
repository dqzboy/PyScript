import psutil
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 定义邮件发送信息
mail_host = 'smtp.example.com'  # 发件人邮箱SMTP服务器地址
mail_user = 'your_email@example.com'  # 发件人邮箱账号
mail_pass = 'your_password'  # 发件人邮箱密码
receivers = ['recipient1@example.com', 'recipient2@example.com']  # 收件人邮箱账号

# 获取系统资源使用情况
cpu_percent = psutil.cpu_percent(interval=1)  # CPU占用率
memory = psutil.virtual_memory()  # 内存使用情况
memory_percent = memory.percent  # 内存使用率
memory_used = round(memory.used / 1024 / 1024 / 1024, 2)  # 内存使用量（GB）
memory_total = round(memory.total / 1024 / 1024 / 1024, 2)  # 内存总量（GB）
disk = psutil.disk_usage('/')  # 磁盘使用情况
disk_percent = disk.percent  # 磁盘使用率
disk_used = round(disk.used / 1024 / 1024 / 1024, 2)  # 磁盘使用量（GB）
disk_total = round(disk.total / 1024 / 1024 / 1024, 2)  # 磁盘总量（GB）

# 构造邮件内容
mail_content = f"""
<h3>系统资源使用情况</h3>
<p>CPU占用率：{cpu_percent}%</p>
<p>内存使用率：{memory_percent}%</p>
<p>内存使用量：{memory_used}GB</p>
<p>内存总量：{memory_total}GB</p>
<p>磁盘使用率：{disk_percent}%</p>
<p>磁盘使用量：{disk_used}GB</p>
<p>磁盘总量：{disk_total}GB</p>
"""

# 构造邮件
message = MIMEText(mail_content, 'html', 'utf-8')
message['From'] = Header(mail_user)
message['To'] = Header(','.join(receivers))
subject = 'Linux系统资源使用情况'
message['Subject'] = Header(subject)

try:
    # 发送邮件
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 25)
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(mail_user, receivers, message.as_string())
    smtpObj.quit()
    print("邮件发送成功")
except smtplib.SMTPException as e:
    print("邮件发送失败：", e)

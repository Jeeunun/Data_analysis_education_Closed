import os                                           
from smtplib import SMTP                            
from email.mime.text import MIMEText                
from email.mime.application import MIMEApplication  
from email.mime.multipart import MIMEMultipart      

def sendMail(from_addr, to_addr, subject, content, files=[]): 
    content_type = "plain"
    username = "hwill1113@naver.com"
    password = "Hanwd201621613"
    # smtp = "smtp.gmail.com"
    # port = 587
    smtp = "smtp.naver.com"
    port = 465

    msg = MIMEMultipart()
    msg['Subject'] = subject  
    msg['From'] = from_addr   
    msg['To'] = to_addr      
    msg.attach(MIMEText(content, content_type))

    if files:
        for f in files:       
            with open(f, 'rb') as a_file:            
                basename = os.path.basename(f)         
                part = MIMEApplication(a_file.read(), Name=basename)         
                part['Content-Disposition'] = 'attachment; flename="%s"' % basename           
                msg.attach(part)

    mail = SMTP(smtp)# 메일 서버 접속
    mail.ehlo()# 메일 서버 연동 설정
    mail.starttls()# 메일 서버 로그인
    mail.login(username, password)# 메일 보내기
    mail.sendmail(from_addr, to_addr, msg.as_string())# 메일 서버 접속 종료
    mail.quit()

if __name__ == "__main__":
    sendMail("hwill1113@naver.com","hanjieun7290@gmail.com",
             "제목입니다.","내용입니다.")
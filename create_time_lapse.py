import os
import time
import cv2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def sendEmail():
    email_user = 'trentdouglasemail@gmail.com'
    email_password = 'ukjsgtrsguedwcxr'
    email_send = 'trentdouglasemail@gmail.com'

    subject = 'Today\'s time lapse'

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    body = '\n'
    msg.attach(MIMEText(body,'plain'))

    filename='./time_lapse_pics/time_lapse.mp4'
    attachment  =open(filename,'rb')

    part = MIMEBase('application','octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= time_lapse.mp4")

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(email_user,email_password)


    server.sendmail(email_user,email_send,text)
    server.quit()

def make_time_lapse():
    image_folder = './time_lapse_pics'
    video_name = 'time_lapse.avi'

    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
    images.sort()
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter("./time_lapse_pics/" + video_name, 0, 40, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()
    
def take_picture(name):
    response = requests.get("http://192.168.0.20:8084/?action=snapshot")
    img = response.content
    file_name = "./time_lapse_pics/" + str(name) + ".jpg"
    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            file.write(response.content)
        img = Image.open(file_name)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        text_position = (10, 10)
        text_color = (255, 255, 255)
        draw.text(text_position, timestamp, font=font, fill=text_color)
        img.save(file_name)
    else:
        print(f"ERROR: {response.status_code}: {response.text}")

## MAIN ##
while True:
    count = 0
    if(time.localtime().tm_hour >= 6 and time.localtime().tm_hour < 21):
        try:
            while (time.localtime().tm_hour >= 6 and time.localtime().tm_hour < 21):
                print("waiting for %15==0 seconds. Current second is " + str(time.localtime().tm_sec))
                #take picture 4 times per minute
                seconds = time.localtime().tm_sec
                if(seconds == 0 or seconds == 15 or seconds == 30 or seconds == 45):
                    os.system("clear")
                    take_picture("pic_" + str("%06d"%(count,)))       
                    count = count + 1
                time.sleep(1)
        except:
            pass
    
        file_name_with_time = str(time.localtime().tm_mon).zfill(2) + "-" + str(time.localtime().tm_mday).zfill(2) + "-" + str(time.localtime().tm_year) + ".mp4"
        make_time_lapse()
        print("\nTime Lapse Created, Converting to MP4\n")
        os.system('ffmpeg -i ./time_lapse_pics/time_lapse.avi -c:v h264 -b:v 200k -y ./time_lapse_pics/time_lapse.mp4')
        # os.system('ffmpeg -i ./time_lapse_pics/time_lapse.avi -c:v copy -c:a copy ./time_lapse_pics/time_lapse.mp4')
        print("\nVideo Successfully converted to MP4! Sending email...\n")
        sendEmail()
        print("Email Sent")
        print("Moving to Web Server...")
        os.system(f'cp ./time_lapse_pics/time_lapse.mp4 /home/trent/dashboard/public/assets/time_lapses/{file_name_with_time}')
        print("Deleting artifacts")
        os.system('rm time_lapse_pics/*')
        print("Done")
    else:
        print("Waiting until 6:00 AM. Current time is ")
        os.system('date')
        print("Waiting one minute...")
        time.sleep(60)
    

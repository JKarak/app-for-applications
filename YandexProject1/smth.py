import smtplib


smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
smtpObj.starttls()

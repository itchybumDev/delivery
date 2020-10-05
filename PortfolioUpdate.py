import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendEmail(row_body, email_address):
    sender_email = "buffolio.bot@gmail.com"
    receiver_email = email_address
    password = "2wdcft6!"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Portfolio Report"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    # text = """\
    # PORFOLIO:
    # {table}

    # """

    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <style type="text/css">
          table {
            background: white;
            border-radius:3px;
            border-collapse: collapse;
            height: auto;
            max-width: 900px;
            padding:5px;
            width: 100%;
            animation: float 5s infinite;
          }
          th {
            color:#FFF8F4;
            background:#E7717D;
            border: solid 1px #656565;
            font-size:14px;
            font-weight: 600;
            padding:10px;
            text-align:center;
            vertical-align:middle;
          }
          tr {
            border: solid 1px #656565;
            color:black;
            font-size:16px;
            font-weight:normal;
          }
          tr:hover td {
            background:#4E5066;
            color:#FFFFFF;
            border-top: 1px solid #22262e;
          }
          td {
            background:#F8F6F7;
            padding:10px;
            text-align:left;
            vertical-align:middle;
            font-weight:300;
            font-size:13px;
            border-right: 1px solid #C1C3D1;
          }
        </style>
      </head>
      <body>
        <br> <br>
        My Portfolio Report<br><br>
        <table>
          <thead>
            <tr style="border: 1px solid #1b1e24;">
              <th>Stock</th>
              <th>Q.ty</th>
              <th>Paid</th>
              <th>Curr. Price</th>
              <th>Daily Chg</th>
              <th>Profit/Loss</th>
            </tr>
          </thead>
          <tbody>
          """

    #     row = """
    #             <tr>
    #               <td>AMZN</td>
    #               <td>100</td>
    #               <td>3</td>
    #               <td>4</td>
    #               <td>5</td>
    #               <td>6</td>
    #             </tr>
    #         """

    end = """
          </tbody>
        </table>
        <br>
        Share this bot: https://t.me/Buffolio_Bot
        <br>
        Thank you!
      </body>
    </html>
    """

    # text = text.format(table=tabulate(data))

    # Turn these into plain/html MIMEText objects
    # part1 = MIMEText(text, "plain")
    part2 = MIMEText(html + row_body + end, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    # message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def generate_email(my_portfolio, email_address):
    row_body = ""
    sendEmail(row_body, email_address)
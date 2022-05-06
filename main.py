import json
import requests
import random
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi import FastAPI, Request, Form
import sentry_sdk
from sentry_sdk import start_transaction
import os

sentry_sdk.init(
    dsn=f"{sentry_key}",
    traces_sample_rate=1.0,
)

path = "/root/steam_proof_creator-main/steam_auto_proof/"

templates = Jinja2Templates(directory="templates")
created_templates = Jinja2Templates(directory="templates/created_gifts")
app = FastAPI()


def proof_creator(name, steamid, purchasedate):

    with open(path + "gift.html", "r") as file:
        html_file = file.read()

    url = f"""http://api.steampowered.com/ISteamUser
               /GetPlayerSummaries/v0002/?key={steam_api}
               &steamids={steamid}"""

    response = requests.request("GET", url, headers={}, data={})
    response_json = json.loads(response.text)

    steam_balance = random.uniform(0.00, 250.00)
    notifs = random.randint(1, 9)

    try:
        steam_username = response_json["response"]["players"][0]["personaname"]
        steam_avatar = response_json["response"]["players"][0]["avatar"]
        error_code = {"error": False, "errorCode": None, "errorType": None}
    except IndexError:
        error_code = {
            "error": True,
            "errorCode": f"Steam ID {steamid} doesn't exist.",
            "errorType": 404,
        }
        return error_code

    except Exception as Error:
        error_code = {
            "error": True,
            "errorCode": (str(error)),
            "errorType": (str(type(error))),
        }
        return error_code

    filedata = html_file.replace("ideals", f"{steam_username}")
    filedata = filedata.replace("R6", name)
    filedata = filedata.replace(
        """https://steamcdn-a.akamaihd.net/steamcommunity
                                    /public/images/avatars/9b/9b5f839661e0b7052d6
                                    324c31aa9f6c3183ecf86.jpg""",
        f"{steam_avatar}",
    )
    filedata = filedata.replace("webinfosearch", steam_username)
    filedata = filedata.replace("Feb 11, 2012", purchasedate)
    filedata = filedata.replace("$0.00", (f"${round(steam_balance,2)}"))
    filedata = filedata.replace(
        '<span class="notification_count">3</span>',
        f'<span class="notification_count">{notifs}</span>',
    )

    with open(path + f"templates/created_gifts/gift1.html", "w") as file:
        file.write(filedata)
    return error_code


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info")


@app.get("/steam/", response_class=HTMLResponse)
def write_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/submitform")
async def handle_form(
    request: Request,
    name: str = Form(...),
    steamid: str = Form(...),
    purchasedate: str = Form(...),
):
    with start_transaction(op="task", name="proof_image_creator"):
        error_code = proof_creator(name, steamid, purchasedate)
    if error_code["error"] == False:
        return created_templates.TemplateResponse(f"gift1.html", {"request": request})
    else:
        return error_code


sentry_key = os.getenv("sentry")
steam_api = os.getenv("steamkey")

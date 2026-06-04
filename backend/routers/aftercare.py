from fastapi import APIRouter
from models.schemas import AftercareInput, AftercareOutput

router = APIRouter(prefix="/api/aftercare", tags=["Aftercare"])

CONTENT = {
    "en": {
        "Miscarriage": {
            "emotional": (
                "What you are feeling is completely valid. A miscarriage is a real loss "
                "and grief takes many forms — sadness, anger, numbness, or guilt. "
                "All of these are normal. You are not alone, and this was not your fault."
            ),
            "physical": (
                "You may experience bleeding and cramping for up to 2 weeks. "
                "Rest as much as possible. Stay hydrated and eat nutritious food. "
                "Avoid strenuous activity for at least 1 week. "
                "Use sanitary pads — not tampons — until bleeding stops."
            ),
        },
        "Abortion": {
            "emotional": (
                "Your feelings about this experience are valid — whatever they are. "
                "Some women feel relief, others feel grief, and many feel both. "
                "There is no right way to feel. Confidential support is available."
            ),
            "physical": (
                "Light bleeding for up to 2 weeks is normal. "
                "Take any prescribed medication as directed. "
                "Rest for the first 24–48 hours. "
                "Avoid intercourse until bleeding has fully stopped."
            ),
        },
        "Still Birth": {
            "emotional": (
                "The loss of your baby is a profound grief. "
                "Give yourself time and space to mourn. "
                "Reach out to a counsellor or support group when you are ready — "
                "you do not have to carry this alone."
            ),
            "physical": (
                "Your body will need significant time to recover. "
                "Follow all discharge instructions from your health provider. "
                "Watch for signs of infection and return to the facility immediately "
                "if you develop a fever, heavy bleeding, or severe pain."
            ),
        },
        "Refusal": {
            "emotional": (
                "We understand there may be many reasons care was not accessed. "
                "You are still deserving of support and information. "
                "A CHV or health worker can visit you privately if that helps."
            ),
            "physical": (
                "Please monitor your body closely. "
                "If you experience heavy bleeding, severe pain, fever, "
                "or foul-smelling discharge, seek care immediately — "
                "these are signs of a complication that needs treatment."
            ),
        },
    },
    "sw": {
        "Miscarriage": {
            "emotional": (
                "Hisia zako ni za kawaida kabisa. Kupoteza mimba ni hasara ya kweli "
                "na huzuni inaweza kujidhihirisha kwa njia nyingi. Hukupaswa kupitia "
                "hili peke yako."
            ),
            "physical": (
                "Unaweza kupata kutokwa na damu na maumivu kwa wiki mbili. "
                "Pumzika na unywe maji mengi. "
                "Tumia pedi za usafi — si tamponi — hadi damu itakapokoma."
            ),
        },
        "Abortion": {
            "emotional": (
                "Hisia zako kuhusu uzoefu huu ni za kawaida. "
                "Wengine wanahisi faraja, wengine huzuni, na wengi wanahisi vyote viwili. "
                "Msaada wa siri unapatikana."
            ),
            "physical": (
                "Kutokwa na damu kidogo kwa wiki mbili ni kawaida. "
                "Chukua dawa zote zilizowekwa. "
                "Pumzika masaa 24–48 ya kwanza."
            ),
        },
        "Still Birth": {
            "emotional": (
                "Kupoteza mtoto wako ni huzuni kubwa. "
                "Jipe muda wa kuomboleza. "
                "Mshauri au kikundi cha msaada kinaweza kukusaidia."
            ),
            "physical": (
                "Mwili wako unahitaji muda wa kupona. "
                "Fuata maelekezo yote ya kituo cha afya. "
                "Rudi haraka ukipata homa, kutokwa na damu nyingi, au maumipu makali."
            ),
        },
        "Refusal": {
            "emotional": (
                "Tunaelewa kunaweza kuwa na sababu nyingi. "
                "Bado unastahili msaada na taarifa. "
                "CHV anaweza kukutembelea kibinafsi."
            ),
            "physical": (
                "Tafadhali angalia mwili wako kwa makini. "
                "Ukipata damu nyingi, maumivu makali, au homa — "
                "tafuta huduma haraka."
            ),
        },
    },
}

WARNING_SIGNS = [
    "Heavy bleeding (soaking more than 1 pad per hour)",
    "Fever above 38°C / 100.4°F",
    "Severe abdominal pain or cramping",
    "Foul-smelling vaginal discharge",
    "Dizziness, fainting, or difficulty breathing",
    "No improvement after 48 hours",
]

RESOURCES = [
    "Kenya Red Cross Psychosocial Support Line: 1199",
    "Marie Stopes Kenya: +254 709 992 000",
    "Reproductive Health Network Kenya: rhnek.org",
    "Befrienders Kenya (emotional support): +254 722 178 177",
]


@router.post("/support", response_model=AftercareOutput,
             summary="Get culturally sensitive aftercare guidance")
def get_aftercare(data: AftercareInput):
    lang     = data.language if data.language in CONTENT else "en"
    content  = CONTENT[lang].get(data.loss_type, CONTENT[lang]["Miscarriage"])

    follow_up = (
        "Return to a health facility within 2 weeks for a follow-up check. "
        "Contact your CHV within 48 hours if any warning signs appear."
    )
    if data.risk_level == "HIGH":
        follow_up = (
            "Seek care at a health facility TODAY. "
            "Do not wait — complications from untreated pregnancy loss "
            "can become life-threatening within hours."
        )

    return AftercareOutput(
        language=lang,
        emotional_support=content["emotional"],
        physical_guidance=content["physical"],
        warning_signs=WARNING_SIGNS,
        follow_up=follow_up,
        resources=RESOURCES,
    )


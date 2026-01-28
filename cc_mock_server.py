from fastapi import FastAPI, Form, Query
from fastapi.responses import Response
import uvicorn

app = FastAPI(title="Creative Commons API Mock", version="1.5")


# WORKFLOW 1: Llista de llicències
@app.get("/")
async def get_licenses(locale: str = Query(default="en")):
    """
    Retorna la llista de llicències disponibles.
    Equivalent a: GET /?locale=ca
    """
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<licenses>
  <license id="standard">Creative Commons</license>
  <license id="publicdomain">Public Domain</license>
  <license id="zero">CC0</license>
  <license id="mark">Public Domain Mark</license>
</licenses>"""
    
    return Response(content=xml, media_type="application/xml")


# WORKFLOW 2: Camps d'una llicència
@app.get("/license/{license_id}")
async def get_license_fields(
    license_id: str,
    locale: str = Query(default="en")
):
    """
    Retorna els camps configurables per una llicència específica.
    Equivalent a: GET /license/standard?locale=ca
    """
    
    if license_id == "standard":
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<license>
  <field id="commercial">
    <label>Allow commercial uses of your work?</label>
    <description>The licensor permits others to copy, distribute and transmit the work. In return, licensees may not use the work for commercial purposes — unless they get the licensor's permission.</description>
    <type>enum</type>
    <enum id="y">
      <label>Yes</label>
    </enum>
    <enum id="n">
      <label>No</label>
    </enum>
  </field>
  <field id="derivatives">
    <label>Allow modifications of your work?</label>
    <description>The licensor permits others to copy, distribute and transmit only unaltered copies of the work — not derivative works based on it.</description>
    <type>enum</type>
    <enum id="y">
      <label>Yes</label>
    </enum>
    <enum id="sa">
      <label>Yes, as long as others share alike</label>
    </enum>
    <enum id="n">
      <label>No</label>
    </enum>
  </field>
</license>"""
    
    elif license_id == "zero":
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<license>
  <field id="confirm">
    <label>I hereby waive all copyright and related or neighboring rights together with all associated claims and causes of action with respect to this work to the extent possible under the law.</label>
    <type>enum</type>
    <enum id="y">
      <label>I agree</label>
    </enum>
  </field>
</license>"""
    
    elif license_id == "publicdomain":
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<license>
  <field id="confirm">
    <label>I certify that the work is in the public domain.</label>
    <type>enum</type>
    <enum id="y">
      <label>I certify</label>
    </enum>
  </field>
</license>"""
    
    else:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<license></license>"""
    
    return Response(content=xml, media_type="application/xml")


# WORKFLOW 3A: Generar llicència amb respostes
@app.post("/license/{license_id}/issue")
async def issue_license(
    license_id: str,
    answers: str = Form(...)
):
    """
    Genera una llicència basada en les respostes de l'usuari.
    Equivalent a: POST /license/standard/issue
    Body: answers=<answers><locale>ca</locale><license-standard><commercial>n</commercial>...
    """
    
    # Mapeja combinacions a URIs de llicències CC
    license_map = {
        ("standard", "y", "y"): ("by", "Attribution 4.0 International"),
        ("standard", "y", "sa"): ("by-sa", "Attribution-ShareAlike 4.0 International"),
        ("standard", "y", "n"): ("by-nd", "Attribution-NoDerivatives 4.0 International"),
        ("standard", "n", "y"): ("by-nc", "Attribution-NonCommercial 4.0 International"),
        ("standard", "n", "sa"): ("by-nc-sa", "Attribution-NonCommercial-ShareAlike 4.0 International"),
        ("standard", "n", "n"): ("by-nc-nd", "Attribution-NonCommercial-NoDerivatives 4.0 International"),
    }
    
    # Extreu commercial i derivatives del XML (parsing simplificat)
    commercial = "y" if "<commercial>y</commercial>" in answers else "n"
    derivatives = "sa" if "<derivatives>sa</derivatives>" in answers else (
        "y" if "<derivatives>y</derivatives>" in answers else "n"
    )
    
    # Gestió de llicències especials
    if license_id == "zero":
        license_code = "zero/1.0"
        license_name = "CC0 1.0 Universal"
    elif license_id == "publicdomain":
        license_code = "publicdomain"
        license_name = "Public Domain"
    else:
        key = (license_id, commercial, derivatives)
        license_code, license_name = license_map.get(
            key, 
            ("by", "Attribution 4.0 International")
        )
    
    # Genera el RDF segons el tipus de llicència
    if license_id == "zero":
        rdf_content = f"""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns:cc="http://creativecommons.org/ns#">
      <cc:License rdf:about="http://creativecommons.org/publicdomain/{license_code}/">
        <cc:permits rdf:resource="http://creativecommons.org/ns#Reproduction"/>
        <cc:permits rdf:resource="http://creativecommons.org/ns#Distribution"/>
        <cc:permits rdf:resource="http://creativecommons.org/ns#DerivativeWorks"/>
      </cc:License>
    </rdf:RDF>"""
        uri = f"http://creativecommons.org/publicdomain/{license_code}/"
    else:
        rdf_content = f"""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns:cc="http://creativecommons.org/ns#">
      <cc:License rdf:about="http://creativecommons.org/licenses/{license_code}/4.0/">
        <cc:permits rdf:resource="http://creativecommons.org/ns#Reproduction"/>
        <cc:permits rdf:resource="http://creativecommons.org/ns#Distribution"/>
        <cc:requires rdf:resource="http://creativecommons.org/ns#Attribution"/>
      </cc:License>
    </rdf:RDF>"""
        uri = f"http://creativecommons.org/licenses/{license_code}/4.0/"
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<result>
  <license-uri>{uri}</license-uri>
  <license-name>{license_name}</license-name>
  <rdf>
    {rdf_content}
  </rdf>
</result>"""
    
    return Response(content=xml, media_type="application/xml")


# WORKFLOW 3B: Detalls d'una URI existent
@app.get("/details")
async def get_license_details(
    license_uri: str = Query(alias="license-uri")
):
    """
    Retorna els detalls d'una llicència donada la seva URI.
    Equivalent a: GET /details?license-uri=http://creativecommons.org/licenses/by-nc-sa/3.0/
    """
    
    # Extreu el tipus de llicència de la URI
    license_types = {
        "/by-nc-sa/": "Attribution-NonCommercial-ShareAlike",
        "/by-nc-nd/": "Attribution-NonCommercial-NoDerivatives",
        "/by-nc/": "Attribution-NonCommercial",
        "/by-sa/": "Attribution-ShareAlike",
        "/by-nd/": "Attribution-NoDerivatives",
        "/by/": "Attribution",
        "/zero/": "CC0",
        "/publicdomain/": "Public Domain",
    }
    
    # Determina la versió
    version = "4.0"
    for v in ["1.0", "2.0", "2.5", "3.0", "4.0"]:
        if f"/{v}/" in license_uri:
            version = v
            break
    
    # Troba el tipus de llicència
    license_name = "Creative Commons License"
    for pattern, name in license_types.items():
        if pattern in license_uri:
            license_name = f"{name} {version} International" if pattern not in ["/zero/", "/publicdomain/"] else name
            break
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<result>
  <license-uri>{license_uri}</license-uri>
  <license-name>{license_name}</license-name>
  <rdf>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns:cc="http://creativecommons.org/ns#">
      <cc:License rdf:about="{license_uri}">
        <cc:permits rdf:resource="http://creativecommons.org/ns#Reproduction"/>
        <cc:permits rdf:resource="http://creativecommons.org/ns#Distribution"/>
      </cc:License>
    </rdf:RDF>
  </rdf>
</result>"""
    
    return Response(content=xml, media_type="application/xml")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "CC Mock API"}


if __name__ == "__main__":
    uvicorn.run(
        "cc_mock_server:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
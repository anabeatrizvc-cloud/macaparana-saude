"""Verificação visual e capturas. Requer playwright apenas no desenvolvimento."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'telas'
OUT.mkdir(parents=True,exist_ok=True)

with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto('http://127.0.0.1:8000')
    page.locator('#login-form').wait_for()
    page.screenshot(path=str(OUT/'01-login.png'),full_page=True)
    page.get_by_role('button',name='Entrar no sistema').click()
    page.locator('.sidebar').wait_for()
    for i,slug in enumerate(['dashboard','patients','requests','calendar','trips','review','finance','fleet','audit','help'],2):
        page.goto('http://127.0.0.1:8000/#'+slug)
        page.locator('#content').wait_for()
        page.wait_for_timeout(250)
        if slug=='finance':
            assert page.locator('#month').bounding_box()['width']>=140, 'Filtro de competência deve permanecer legível'
        if slug=='help':
            page.locator('a[href="/docs/fluxos.html"]').wait_for()
        page.screenshot(path=str(OUT/f'{i:02}-{slug}.png'),full_page=True)
        assert page.locator('h1').count()==1,slug
    page.goto('http://127.0.0.1:8000/#trips')
    page.locator('[data-act="trip-detail"]').first.click()
    page.locator('dialog[open]').wait_for()
    page.screenshot(path=str(OUT/'12-operacao.png'),full_page=True)
    page.get_by_role('button',name='Fechar',exact=True).click()
    page.set_viewport_size({'width':390,'height':844})
    page.goto('http://127.0.0.1:8000/#dashboard')
    page.screenshot(path=str(OUT/'13-mobile.png'),full_page=False)
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Overflow mobile'
    assert not errors,errors
    print(json.dumps({'screenshots':13,'javascript_errors':errors,'mobile_width':390,'result':'PASS'},ensure_ascii=False))
    browser.close()

# Questionário (ESTADO_CIVIL, TIPO/UF/ANO_ENSINO_MEDIO) persistence in cadastros.form_data + export
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')
CPF = '390.533.447-05'
CPF_DIGITS = '39053344705'
FD = {
    'NOME': 'TEST QUEST API', 'CPF': CPF, 'EMAIL': 'teste@example.com', 'SEXO': '2',
    'ESTADO_CIVIL': 'Casado', 'TIPO_ENSINO_MEDIO': 'Magistério',
    'UF_ENSINO_MEDIO': 'Demais estados ou outros países', 'ANO_ENSINO_MEDIO': '2027 ou após',
}


@pytest.fixture(scope='module')
def admin():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/admin/auth/login", json={'username': 'donas', 'password': 'Seinao10@@'})
    if r.status_code != 200:
        pytest.skip('admin login failed')
    s.headers['Authorization'] = f"Bearer {r.json()['token']}"
    yield s
    for c in (CPF, CPF_DIGITS):
        s.delete(f"{BASE_URL}/api/admin/cadastros/{c}")


def _find(admin):
    for c in (CPF_DIGITS, CPF):
        r = admin.get(f"{BASE_URL}/api/admin/cadastros/{c}/details")
        if r.status_code == 200:
            return r.json()
    return None


def test_track_registration_persists_questionario(admin):
    r = requests.post(f"{BASE_URL}/api/track/registration", json={
        'page': '/inscricao.html', 'user_agent': 'pytest',
        'extra': {'nome': FD['NOME'], 'cpf': CPF, 'email': FD['EMAIL'], 'stage': 'cadastro',
                  'concurso': 'Vestibular Unesp 2027 - Fundação VUNESP', 'visitor_id': 'v_test_q', 'form_data': FD}})
    assert r.status_code == 200
    d = _find(admin)
    assert d is not None, 'cadastro details not found'
    blob = str(d)
    for k in ('ESTADO_CIVIL', 'TIPO_ENSINO_MEDIO', 'UF_ENSINO_MEDIO', 'ANO_ENSINO_MEDIO'):
        assert FD[k] in blob, f"{k} missing in details"


def test_export_full_contains_questionario(admin):
    r = admin.get(f"{BASE_URL}/api/admin/cadastros/export-full.txt", params={'q': 'TEST QUEST API'})
    assert r.status_code == 200
    txt = r.text
    assert 'TEST QUEST API' in txt
    for k in ('ESTADO_CIVIL', 'TIPO_ENSINO_MEDIO', 'UF_ENSINO_MEDIO', 'ANO_ENSINO_MEDIO'):
        assert FD[k] in txt, f"export-full.txt missing {k} value"

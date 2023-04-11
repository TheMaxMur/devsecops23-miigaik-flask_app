from dip import create_app
from dip.extensions import db

      
def test_login():
    app=create_app()
    client=app.test_client()
    response = client.post('/login', data=dict(username='admin',password='admin'))
    assert response.status_code == 302

def test_home_page():
    app=create_app()
    client=app.test_client()
    response=client.get('/')
    assert response.status_code == 200

def test_wiki():
    app=create_app()
    client=app.test_client()
    response = client.post('/login', data=dict(username='admin',password='admin'))
    response=client.get('/wiki')
    assert response.status_code == 200
    

    
def test_new_job_title_gui():
    app=create_app()
    client=app.test_client()
    response = client.post('/login', data=dict(username='admin',password='admin'))    
    response = client.post('/admin/dashboard/job-titles', data=dict(job_title='test'))
    assert response.status_code == 302   

def test_logout():
    app=create_app()
    client=app.test_client()
    response=client.get('/logout')
    assert response.status_code == 302

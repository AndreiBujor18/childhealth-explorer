"""The client shell and modules can load even when database access is forbidden."""
def test_page_shell_and_javascript_have_no_database_dependency(client):
    response = client.get('/period-averages')
    assert response.status_code == 200
    assert 'id="country-list"' in response.text and '<noscript>' in response.text
    assert 'period-averages-page.js' in response.text
    assert 'chart.js@4.4.1' in response.text and 'id="averages-table"' in response.text
    for name in ('api-client', 'period-averages-model', 'period-averages-view', 'period-averages-page'):
        script = client.get(f'/static/js/{name}.js')
        assert script.status_code == 200 and 'javascript' in script.headers['content-type']
    assert '/period-averages' not in client.get('/api/openapi.json').json()['paths']

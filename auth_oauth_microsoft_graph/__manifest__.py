# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Microsoft Graph Oauth Authentication',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': ' Open for Small Business Ltd',
    'website': 'https://o4sb.com',
    'description': """
Allow users to login using Microsoft Graph.
===========================================

Provider name: AzureAD
Client ID: Client ID provided when registering Application
Body: Login with Microsoft
Auth URL: https://login.microsoftonline.com/common/oauth2/v2.0/authorize
Scope: User.Read User.ReadBasic.All
Validation URL: https://graph.microsoft.com/v1.0/me

""",
    'depends': ['auth_oauth'],
}

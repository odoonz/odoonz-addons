# -*- coding: utf-8 -*-
# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
import jwt
import urllib.request, urllib.error, urllib.parse
import json

from odoo import models, fields, api

PEMSTART = "-----BEGIN CERTIFICATE-----\n"
PEMEND = "\n-----END CERTIFICATE-----\n"


class AuthOauthProvider(models.Model):
    _inherit = 'auth.oauth.provider'

    flow = fields.Selection([('access_token', 'OAuth2'),
                             ('id_token', 'OpenID Connect (Azure)')],
                            string='Auth Flow',
                            required=True,
                            default='access_token')

    token_map = fields.Char(
        help="Some Oauth providers don't map keys in their responses "
             "exactly as required.  It is important to ensure user_id and "
             "email at least are mapped. For OpenID Connect user_id is "
             "the sub key in the standard.")

    jwt_keys = fields.One2many(
        comodel_name='jwt.key',
        inverse_name='provider_id',
        string='Authorized Keys',
    )

    validation_endpoint = fields.Char(
        help='For OpenID Connect this should be the location for public keys '
             'e.g. https://login.microsoftonline.com/<tenant_id>/discovery/'
             'keys')

    @api.multi
    def _refresh_keys(self):
        """
        We store the keys for performance. They don't change much
        """

        for provider in self:
            if provider.flow != 'id_token':
                continue
            f = urllib.request.urlopen(provider.validation_endpoint)
            response = json.loads(f.read())
            provider.jwt_keys = self.env['jwt.key']
            keys_to_write = []
            for k in response.get('keys', []):
                keys_to_write.append((0, 0, {
                    'x5t': k['x5t'],
                    'kid': k['kid'],
                    'x5c': k['x5c'][0]
                }))
            provider.write({'jwt_keys': keys_to_write})

    @api.multi
    def _parse_id_token(self, id_token):
        self.ensure_one()
        res = {}
        header = jwt.get_unverified_header(id_token)
        key = self.jwt_keys.filtered(
            lambda r: r.x5t == header['x5t'] and r.kid == header['kid'])
        if not key:
            self._refresh_keys()
            key = self.jwt_keys.filtered(
                lambda r: r.x5t == header['x5t'] and r.kid == header['kid'])
        if key:
            res.update(jwt.decode(id_token, key.pubkey(), algorithms=['RS256'],
                                  audience=self.client_id))
            if self.token_map:
                for pair in self.token_map.split(' '):
                    from_key, to_key = pair.split(':')
                    if to_key not in res:
                        res[to_key] = res.get(from_key, '')
        return res


class JWTKeys(models.Model):
    _name = 'jwt.key'
    _rec_name = 'x5t'

    provider_id = fields.Many2one(
        comodel_name='auth.oauth.provider')
    x5t = fields.Char()
    x5c = fields.Char()
    kid = fields.Char()

    @api.multi
    def pubkey(self):
        self.ensure_one()
        cert_str = str(PEMSTART + self.x5c + PEMEND)
        cert_obj = load_pem_x509_certificate(cert_str, default_backend())
        return cert_obj.public_key()

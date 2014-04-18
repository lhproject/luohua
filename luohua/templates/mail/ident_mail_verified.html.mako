## -*- coding: utf-8 -*-
<%inherit file="base.html.mako" />
<%namespace name="common" file="utils.common.mako" />
<%namespace name="utils" file="utils.html.mako" />

<%block name="title">邮箱验证通过</%block>

<%block name="recipient">${display_name}</%block>

<%block name="content">
<%utils:p>您的注册邮箱已经验证通过，江南听雨网热烈欢迎您的到来！</%utils:p>
<%utils:button href="${capture(common.frontend_url, '/')}">四处看看去</%utils:button>
</%block>


<%block name="footbox">
</%block>


<!-- vim:set ai et ts=2 sw=2 sts=2 fenc=utf-8 syn=mako: -->

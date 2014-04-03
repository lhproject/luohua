## -*- coding: utf-8 -*-
<%inherit file="base.html.mako" />
<%namespace name="utils" file="utils.html.mako" />

<%block name="title">验证邮箱</%block>

<%block name="recipient">小伙伴</%block>

<%block name="content">
<%utils:p>感谢您注册江南听雨网帐户，请您点击下面的按钮验证注册邮箱：</%utils:p>
<%utils:button href="${url}">现在去验证</%utils:button>
</%block>


<%block name="footbox">
</%block>


<!-- vim:set ai et ts=2 sw=2 sts=2 fenc=utf-8 syn=mako: -->

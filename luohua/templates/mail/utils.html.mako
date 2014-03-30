## -*- coding: utf-8 -*-
<%!
import time

import weiyu
import luohua


def now():
    return time.time()


def cvt_timestamp(timestamp):
    return time.localtime(int(timestamp) if timestamp != 'None' else now())


def for_time_elem(timestamp=None):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', cvt_timestamp(timestamp))


def for_time_elem_text(timestamp=None):
    return time.strftime('%Y-%m-%d', cvt_timestamp(timestamp))
%>


<%def name="weiyu_version()">${weiyu.VERSION_STR}</%def>


<%def name="luohua_version()">${luohua.__version__}</%def>


<%def name="time_elem(ts=None)"><time datetime="${ts | for_time_elem}">${ts | for_time_elem_text}</time></%def>


<%def name="aux_link(link)">
<p class="p-minor">
如果点击无效，请复制下方网页地址到浏览器地址栏中打开：<br />
<a href="${link}" class="lnk-minor">${link | h}</a>
</p>
</%def>


<%def name="button(href)">
<a href="${href}" class="button">
  <span class="button__link">${caller.body() | trim,h}</span>
</a>
${aux_link(href)}
</%def>


<!-- vim:set ai et ts=2 sw=2 sts=2 fenc=utf-8 syn=mako: -->

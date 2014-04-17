## -*- coding: utf-8 -*-
<%!
import time

import weiyu
import luohua

from luohua.utils import urls


def now():
    return time.time()


def cvt_timestamp(timestamp):
    return time.localtime(int(timestamp) if timestamp != 'None' else now())
%>


<%def name="machine_readable_time(timestamp=None)">${time.strftime('%Y-%m-%dT%H:%M:%SZ', cvt_timestamp(timestamp))}</%def>


<%def name="for_date_text(timestamp=None)">${time.strftime('%Y-%m-%d', cvt_timestamp(timestamp))}</%def>


<%def name="weiyu_version()">${weiyu.VERSION_STR}</%def>


<%def name="luohua_version()">${luohua.__version__}</%def>


<%def name="frontend_url(s)">${urls.get_frontend_url(s)}</%def>


<!-- vim:set ai et ts=2 sw=2 sts=2 fenc=utf-8 syn=mako: -->

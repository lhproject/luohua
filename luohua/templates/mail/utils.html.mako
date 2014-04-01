## -*- coding: utf-8 -*-
<%namespace name="common" file="utils.common.mako" />


<%def name="time_elem(ts=None)"><time datetime="${common.machine_readable_time(ts)}">${common.for_date_text(ts)}</time></%def>


<%def name="p(style='')"><tr><td><p style="margin: 16px 0;${style}">${caller.body()}</p></td></tr></%def>
<%def name="p_minor(style='')"><%self:p style="font-size: 12px;${style}">${caller.body()}</%self:p></%def>

<%def name="_lnk(href, style)"><a href="${href}" style="${style}">${caller.body() | trim,h}</a></%def>


<%def name="lnk(href)"><%self:_lnk href="${href}" style="color: #08c;">${caller.body()}</%self:_lnk></%def>
<%def name="lnk_minor(href)"><%self:_lnk href="${href}" style="color: #808080;">${caller.body()}</%self:_lnk></%def>
<%def name="footbox_lnk(href)"><%self:_lnk href="${href}" style="color: #95bddc;">${caller.body()}</%self:_lnk></%def>


<%def name="aux_link(href)">
<%self:p_minor>
  如果点击无效，请复制下方网页地址到浏览器地址栏中打开：<br />
  <%self:lnk_minor href="${href}">${href}</%self:lnk_minor>
</%self:p_minor>
</%def>


<%def name="button(href)">
<tr>
  <td>
    <a href="${href}" style="display: inline-block; color: #fff; background-color: #5bbc1b; border-radius: 3px; padding: 10px 20px; font-size: 14px; text-decoration: none;">${caller.body() | trim,h} &raquo;</a>
  </td>
</tr>
${aux_link(href)}
</%def>


<%def name="foot_p(style='')"><tr><td align="center"><p style="margin: 0;${style}">${caller.body()}</p></td></tr></%def>


<%def name="foot_lnk(href)"><%self:_lnk href="${href}" style="color: #999;">${caller.body()}</%self:_lnk></%def>


<!-- vim:set ai et ts=2 sw=2 sts=2 fenc=utf-8 syn=mako: -->

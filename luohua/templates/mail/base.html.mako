## -*- coding: utf-8 -*-
<%namespace name="common" file="utils.common.mako" />
<%namespace name="utils" file="utils.html.mako" />
<!DOCTYPE html>
<html lang="cmn">
<head>
  <meta charset="utf-8">
  <title><%block name="title" /> - JNRain</title>
</head>
<body style="background-color: #fff; color: #262626; margin: 0; padding: 0;">
  <table width="760" align="center" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td style="background-color: #5bbc1b;">
      <table border="0" cellspacing="0" cellpadding="0">
        <tr>
          <td width="24"></td>
          <td width="141" height="50"><img src="http://static.jnrain.com/common/img/logo-141x50-w.png" alt="JNRain" width="141" height="50" style="display: block; margin: 0;" /></td>
          <td width="595" align="right" valign="middle" style="color: #fff; padding-right: 10px; font-size: 16px;">${self.title()}</td>
        </tr>
      </table>
    </td>
  </tr>

  <tr>
    <td style="background-color: #ebebeb;">
      <table width="740" align="center" border="0" cellspacing="0" cellpadding="0">
        <tr>
          <td style="background-color: #fcfcfc;">
            <table width="100%" border="0" cellspacing="0" cellpadding="0">
              <tr><td height="36" colspan="4"></td></tr>
              <tr>
                <td width="30"></td>
                <td colspan="3"><p style="font-size: 16px; font-weight: bold; margin: 0;">尊敬的<span class="mail__recipient"><%block name="recipient" /></span>，您好！</p></td>
              </tr>
              <tr><td height="30" colspan="4"></td></tr>

              <tr>
                <td width="30"></td>
                <td width="33"></td>
                <td colspan="2" style="font-size: 14px; line-height: 1.5;">
                  <table border="0" cellspacing="0" cellpadding="0">
                    <%block name="content" />
                  </table>
                </td>
              </tr>

              <tr><td height="12" colspan="4"></td></tr>
              <tr>
                <td align="right" colspan="3" style="color: #999; font-size: 12px; line-height: 1.5;">
                  <p style="margin: 0;">江南听雨网<br />${utils.time_elem(curtime)}</p>
                </td>
                <td width="30"></td>
              </tr>
              <tr><td height="12" colspan="4"></td></tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <tr>
    <td style="color: #959595; background-color: #ebebeb; font-size: 12px; line-height: 25px; padding: 20px 0 10px 1em;">
      <%block name="footbox" />
    </td>
  </tr>

  <tr><td height="42"></td></tr>

  <tr>
    <td align="center">
      <table width="700" border="0" cellspacing="0" cellpadding="0" style="color: #999; font-size: 12px; line-height: 1.3em;">
        <tr><td height="1" style="background-color: #ccc;"></td></tr>
        <tr><td height="12"></td></tr>

        <%utils:foot_p>江南听雨网系统自动发送, 请不要回复</%utils:foot_p>
        <tr><td height="30"></td></tr>

        <%utils:foot_p>
          &copy; 2013-2014 <%utils:foot_lnk href="//jnrain.com/">江南听雨网</%utils:foot_lnk><br />
          <span style="color: #ddd;">luohua ${common.luohua_version()} | weiyu ${common.weiyu_version()}</span>
        </%utils:foot_p>
      </table>
    </td>
  </tr>

  <tr><td height="20"></td></tr>
</table>
</body>
<!-- vim:set ai et ts=2 sw=2 sts=2 fenc=utf-8 syn=mako: -->
</html>

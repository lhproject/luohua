## -*- coding: utf-8 -*-
<%namespace name="utils" file="utils.html.mako" />
<!DOCTYPE html>
<html lang="cmn">
<head>
  <meta charset="utf-8">
  <title><%block name="title" /> - JNRain</title>

  <style>
<%include file="reset.css" />
<%include file="normalize.css" />
<%include file="base.css" />
<%block name="stylesheets" />
  </style>
</head>
<body>
<article class="mail">
  <header class="mail__hdr">
    <h1 class="mail__hdr__title">${self.title()}</h1>
    <div class="mail__hdr__logo"></div>
  </header>
  <section class="mail__content">
    <p class="mail__content__opening">尊敬的<span class="mail__recipient"><%block name="recipient" /></span>，您好！</p>
    <section class="mail__content__body">
      <%block name="content" />
    </section>
    <p class="mail__content__closing">
    江南听雨网<br />
    ${utils.time_elem(curtime)}
    </p>
  </section>
  <footer class="mail__footbox">
    <%block name="footbox" />
  </footer>
</article>

<footer class="foot">
  <p class="foot__noreply-reminder">江南听雨网系统自动发送, 请不要回复</p>
  <p>
  &copy; 2013-2014 <a href="//jnrain.com/" class="foot__link">江南听雨网</a><br />
  <span class="foot__versions">luohua ${utils.luohua_version()} | weiyu ${utils.weiyu_version()}</span>
  </p>
</footer>
</body>
<!-- vim:set ai et ts=2 sw=2 sts=2 fenc=utf-8 syn=mako: -->
</html>

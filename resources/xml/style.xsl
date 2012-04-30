<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
  <html>
    <head>
    <title>SuperTV for XBMC - XML file</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <meta name="keywords" content="iPod,iPhone,free,livetv,webtv,Live TV,Streams,TV Steams,TV,Cable TV,Mobile TV,TV,Live TV,TV Online,Online TV,XBMC,Software,Streams,Stream,RTMP,Internet,SuperTV" />
    <meta name="description" content="SuperTV for XBMC lets you comfortably watch TV from all over the world on your Mac, PC, Apple TV, iPhone or iPad for free. On top of that, it features a gorgeous EPG." />
      <script type="text/javascript"><![CDATA[
          var _gaq = _gaq || [];
          _gaq.push(['_setAccount', 'UA-29885522-2']);
          _gaq.push(['_trackPageview']);

          (function() {
            var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
            ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
            var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
          })();
      ]]></script>
      <LINK REL="stylesheet" TYPE="text/css" HREF="http://twitter.github.com/bootstrap/assets/css/bootstrap.css"/>
  </head>
  <body>
    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <div class="container" style="width: auto;">
           <a class="brand">SuperTV</a>
           <div class="nav-collapse">
             <ul class="nav">
               <li><a href="http://supercloudtv.com/index.html">Home</a></li>
               <li><a href="http://supercloudtv.com/download.php">Download</a></li>
               <li><a href="http://supercloudtv.com/news.html">News</a></li>
               <li class="dropdown" id="menu1">
                   <a class="dropdown-toggle" data-toggle="dropdown" href="#menu1">Discussion <b class="caret"></b></a>
                   <ul class="dropdown-menu">
                     <li><a href="http://forum.xbmc.org/showthread.php?tid=125291">XBMC</a></li>
                     <li><a href="http://forums.plexapp.com/index.php/topic/40469-release-supertv-for-plex/">Plex</a></li>
                   </ul>
                 </li>
               <li><a id='UserGuide' data-toggle="modal" href="#UserGuideModal">User Guide</a></li>
               <li><a href="http://supercloudtv.com/librtmp.html">Updating libRTMP</a></li>
             </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="modal hide fade" id="UserGuideModal">
      <div class="modal-header">
        <a class="close" data-dismiss="modal">&#215;</a>
        <h3>SuperTV User Guide</h3>
      </div>
      <div class="modal-body">
        <p>To view in-depth EPG for any channel, press <code>i</code> or hold <code>Menu</code> on the Apple Remote.<br />
           To change the aspect ratio of the stream, press <code>1</code>.<br />
           To change the channel, press <code>Up</code> or <code>Down</code> to reveal the channel list.<br />
           To change the volume, press <code>Left</code> or <code>Right</code>.<br />
           To view additional options, press <code>c</code> or hold <code>Menu</code> on the Apple Remote.</p>
           <div style='text-align:center;width:530px;padding:auto;'>
              <script type="text/javascript"><![CDATA[<!--
                google_ad_client = "ca-pub-6005609373497493";
                /* #3 */
                google_ad_slot = "7650170803";
                google_ad_width = 468;
                google_ad_height = 60;
              //-->]]>
              </script>
              <script type="text/javascript"
              src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
              </script>
              </div>
      </div>
      <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">Close</a>
      </div>
    </div>
    <div class="container" style="height:100%;margin-top:40px;">
       <div class='row'>
          <div class='span12' style='text-align:center;padding-top:10px;padding-bottom:5px'>
            <script type="text/javascript"><![CDATA[<!--
              google_ad_client = "ca-pub-6005609373497493";
              /* #1 */
              google_ad_slot = "0585375258";
              google_ad_width = 728;
              google_ad_height = 90;
              //-->]]>
            </script>
            <script type="text/javascript" src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
            </script>
          </div>
        </div>
      <div class="row">
        <div class="span12">    
      <table class="table table-striped table-bordered table-condensed">
        <thead>
      <tr>
        <th>Channel</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <xsl:for-each select="streams/stream">
      <tr>
        <td><xsl:value-of select="title"/></td>
        <td>&lt;stream&gt;<br />
        &#160;&#160;&#160;&#160;&lt;title&gt;<xsl:value-of select="title"/>&lt;/title&gt;<br />
        &#160;&#160;&#160;&#160;&lt;swfUrl&gt;<xsl:value-of select="swfUrl"/>&lt;/swfUrl&gt;<br />
        &#160;&#160;&#160;&#160;&lt;link&gt;<xsl:value-of select="link"/>&lt;/link&gt;<br />
        &#160;&#160;&#160;&#160;&lt;pageUrl&gt;&lt;![CDATA[<xsl:value-of select="pageUrl"/>]]&gt;&lt;/pageUrl&gt;<br />
        &#160;&#160;&#160;&#160;&lt;playpath&gt;<xsl:value-of select="playpath"/>&lt;/playpath&gt;<br />
        &#160;&#160;&#160;&#160;&lt;advanced&gt;<xsl:value-of select="advanced"/>&lt;/advanced&gt;<br />
        &#160;&#160;&#160;&#160;&lt;language&gt;<xsl:value-of select="language"/>&lt;/language&gt;<br />
        &#160;&#160;&#160;&#160;&lt;logourl&gt;<xsl:value-of select="logourl"/>&lt;/logourl&gt;<br />
        &#160;&#160;&#160;&#160;&lt;epgid&gt;<xsl:value-of select="epgid"/>&lt;/epgid&gt;<br />
        <xsl:for-each select="backup">
          &#160;&#160;&#160;&#160;&lt;backup&gt;<br />
          &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&lt;swfUrl&gt;<xsl:value-of select="swfUrl"/>&lt;/swfUrl&gt;<br />
          &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&lt;link&gt;<xsl:value-of select="link"/>&lt;/link&gt;<br />
          &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&lt;pageUrl&gt;&lt;![CDATA[<xsl:value-of select="pageUrl"/>]]&gt;&lt;/pageUrl&gt;<br />
          &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&lt;playpath&gt;<xsl:value-of select="playpath"/>&lt;/playpath&gt;<br />
          &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&lt;advanced&gt;<xsl:value-of select="advanced"/>&lt;/advanced&gt;<br />
          &#160;&#160;&#160;&#160;&lt;/backup&gt;<br/>
        </xsl:for-each>
        &lt;/stream&gt;</td>
      </tr>
      </xsl:for-each>
    </tbody>
    </table>
  </div>
</div>
 <div class="row"><div class="span9 offset1"><div class='span2 offset4' style='text-align:center;color:#C0C0C0'>&#169;2012 HansMayer</div></div></div>
</div>
<script src="http://twitter.github.com/bootstrap/assets/js/jquery.js"></script>
<script src="http://twitter.github.com/bootstrap/assets/js/bootstrap-transition.js"></script>
<script src="http://twitter.github.com/bootstrap/assets/js/bootstrap-dropdown.js"></script>
<script src="http://twitter.github.com/bootstrap/assets/js/bootstrap-modal.js"></script>
  </body>
  </html>
</xsl:template>
</xsl:stylesheet>
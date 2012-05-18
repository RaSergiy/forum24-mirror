#coding=UTF-8


forum = { 
    'themes_per_page' : 30,
    'image_caching':    True,
    'alias' : 'drevlepravoslavie.forum24.ru',
    'url' : 'http://drevlepravoslavie.forum24.ru',
    'gifdomen' : 'http://drevlepravoslavie.forum24.ru',
    'avatars':'http://forum24.ru/avr/d/drevlepravoslavie/avatar/',
    'title' : 'Древлеправославие',
    'outdir' : 'drevlepravoslavie.forum24.ru',
    'add_themes' : [ {'id':20, 'after':10, 'title':'Архив'} ],
    'ignore_themes' : [ 10, ],
    'fail_image' : 'img/failed2.png',

    'prefix-country': '<b>Откуда: </b>',
    'prefix-city': ', ',
    'prefix-message_n': '<b>Сообщение: </b>',
    'prefix-zvanie': '',
    'prefix-zamechanie': 'Замечания: ',
    'prefix-userinfo': '<b>Упование: </b>',
    'prefix-registered': '<b>Зарегистрирован: </b>',
    'prefix-sign':'<div class="post-sign">',
    'postfix-sign':'</div>',
}
 

template = {
    'thanks' :  '<p><div class="post-thanks" onmouseover="tooltip.show(\'%(users)s\');" onmouseout="tooltip.hide();">Спаси Христос: %(count)d</div></p>',
    'zamechanie' :  '<img onmouseover="tooltip.show(\'%(text)s\');" onmouseout="tooltip.hide();" src="%(gif)s"/>',
    'head'          : '<html><head>\
    <title>Зеркало форума - %(forum-alias)s</title>\
    <link rel="stylesheet" type="text/css" href="%(forum-relativepath)sstyle.css" media="all"/>\
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\
    <script type="text/javascript" src="%(forum-relativepath)sscripts.js"></script>\
    </head><body><div id="layout"><div id="head"><a href="%(forum-relativepath)sindex.html"><img src="%(forum-relativepath)simg/head.jpg"/></a></div>',

    'content'       : '<div id="content">',
    
    'index'    : '<div class="blockgroup"><h1>Список форумов</h1><table id="forum-list"><colgroup><col/><col width="60"/><col width="60"/></colgroup><tr class="row-first"><th>Форумы</th><th>Тем</th><th>Ответов</th></tr>',
    'blockgroup': '<tr><td colspan="3" class="table-header">%(blockgroup-title)s</td></tr>',
    '/index'   :'</table></div>',

    'blockgroup_block': '<tr class="row-%(block-oddity)s"><td class="theme_title"><a href="data/%(block-filename)s">%(block-title)s</a></td><td class="theme_count">%(block-themes_count)s</td><td class="theme_answers">%(block-answers_count)s</td></tr>',

    'block'         : '<div class="block"><p><a href="../index.html">К началу</a></p><h1>%(block-title)s</h1><table id="forum-list"><colgroup><col/><col width="50"/><col width="100"/><col width="100"/></colgroup><tr class="row-first"><th>Тема</th><th>Ответов</th><th>Создана</th><th>Последний ответ</th></tr>',
    '/block':'</table></div>',

    'block_theme'   : '<tr class="row-%(theme-oddity)s">\
                    <td class="theme_title"><a href="%(theme-filename)s"  class="hotspot"  onmouseover="tooltip.show(\'%(theme-spoiler)s\');" onmouseout="tooltip.hide();">%(theme-title)s</a></td>\
                    <td class="theme_answers">%(theme-answers)s</td>\
                    <td class="theme_author">%(theme-author)s <div class="theme_timestamp">%(theme-timestamp)s</div></td>\
                    <td class="theme_author">%(theme-lastauthor)s <div class="theme_timestamp">%(theme-lasttimestamp)s</div></td>\
    </tr>',


    'tag:more': '<div class="more-block"><div id="more-%(uniqid)s" onclick="moreshow(\'more-%(uniqid)s\');" class="more-link"><a href="#" onclick="return false">Скрытый текст</a></div><div class="more-text" id="more-%(uniqid)s-text" ><span class="indent"></span>%(text)s</div></div>',

    'theme'         : '<div id="nav"><p><a href="../index.html">Архив форума от %(forum-timestamp)s</a> → <a href="%(block-filename)s">%(block-title)s</a> → %(theme-title)s</p></div><table id="posts"><colgroup><col width="120"/><col/></colgroup>',
    '/theme'        : '</table>',
    'post'          : '<tr class="row-%(post-oddity)s"><td class="post-info"><span class="post-author">%(post-author)s</span> <div class="post-infoblock"><span class="post-zvanie">%(post-zvanie)s</span> <span class="post-userinfo">%(post-userinfo)s</span> <span class="post-rang">%(post-rang)s</span> <span class="post-location">%(post-country)s%(post-city)s</span> <span class="post-message_n">%(post-message_n)s</span> <span class="post-registered">%(post-registered)s</span> <span class="post-avatar">%(post-avatar)s</span> <span class="post-zamechanie">%(post-zamechanie)s</div></div></td><td class="post-body"><div class="post-head"><b>Отправлено:</b> %(post-timestamp)s. <b>Заголовок:</b> %(post-title)s</div></div><div class="post-text"><p>%(post-text)s</p></div>%(post-sign)s%(post-thanks)s</td></tr>',

    '/content'      : '</div>',
    '/head'         : '<div id="footer"><p>Зеркало форума <a href="%(forum-url)s">%(forum-url)s</a> от %(forum-timestamp)s</p><p>Исходная страница: <a href="%(forum-source)s">%(forum-source)s</a></p><img src="%(forum-relativepath)simg/footer.jpg"></div></div></body></html>',
        }

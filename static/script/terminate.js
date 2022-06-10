$(function () {
    setTimeout(() => {
        $(".text").fadeOut(0.05);
        $(".text").html("프로그램 종료");
        $(".text").fadeIn(1000);
        $(".loader").fadeOut();
        var create_btn = '<button class="btn_new" style="display:none;" onclick="">오늘의 레포트</button>\n'
        $(".create_btn").html(create_btn);
        $(".create_btn").attr('onclick',"window.location.href='/daily'");
        $(".btn_new").fadeIn(1000);
    }, 5000);
});
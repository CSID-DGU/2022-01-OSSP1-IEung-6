$(function(){
	$(".set > button").click(
		function () {
			$(".set > button:nth-child(n)").removeClass("btn_on");
			$(".set > button:nth-child(n)").addClass("btn_off");
			$(this).addClass("btn_on");
			$(this).removeClass("btn_off");
		}
	);
	
	$(".run > button").click(
		function () {
			$(".run > button:nth-child(n)").removeClass("btn_on");
			$(".run > button:nth-child(n)").addClass("btn_off");
			$(this).addClass("btn_on");
			$(this).removeClass("btn_off");
		}
    );

	$(".set > button:nth-child(1)").click(
		function () {
			$(".wrapper_frame > img:nth-child(n)").hide();
			$(".wrapper_frame > img:nth-child(1)").show();
		}
	);

	$(".set > button:nth-child(2)").click(
		function () {
			$(".wrapper_frame > img:nth-child(n)").hide();
			$(".wrapper_frame > img:nth-child(2)").show();
		}
	);

	$(".set > button:nth-child(3)").click(
		function () {
			$(".wrapper_frame > img:nth-child(n)").hide();
			$(".wrapper_frame > img:nth-child(3)").show();
		}
    );
});
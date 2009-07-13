var init = function () {
    this.img = new Image();
    this.img.src = "/display_image/Location/0/homelogo";
    $('#header').css('backgroundImage', "url(" + this.img.src + ")").css('backgroundPosition', 'top center');
}
$(document).ready(init);

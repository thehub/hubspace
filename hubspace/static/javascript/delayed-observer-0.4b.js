/*
 jQuery delayed observer - 0.4
 (c) 2007 ~ Maxime Haineault (haineault@gmail.com)
 
 MIT License (http://www.opensource.org/licenses/mit-license.php)
 
 changelog
 ---------
 0.2 using closure, special thanks to Stephen Goguen & Tane Piper.
 0.3 now allow object chaining, added license
 0.4 code cleanup, added support for other events than keyup, fixed variable scope

modified by me to actually work with a real callback/action, without having to deal with the timer in the action/callback. befor callback was both the arg passed into delayedObserver and the example. may as well have written this myself really in the end.
*/

(function($) {
  var stack = [];var target;
 
  function callback(pos) {
    target = stack[pos];
    if (target.timer) clearTimeout(target.timer);
   
    target.timer = setTimeout(function(){
      target.timer = null;
      target.action(target.obj.val(), target.obj);
    }, target.delay * 1000);

    target.oldVal = target.obj.val();
  } 
 
  $.fn.extend({
    delayedObserver:function(delay, action, opt){
      var $this = $(this);
      var event = opt.event || 'keyup';
      var pos   = 0;
      
      stack.push({obj: $this, timer: null, delay: delay,
                  oldVal: $this.val(), action:action});
       
      pos = stack.length-1;
     
      $this[event](function() {
        target = stack[pos];
          if (target.obj.val() == target.oldVal) return;
          else callback(pos);
      });
      return this;
    }
  });
})(jQuery);

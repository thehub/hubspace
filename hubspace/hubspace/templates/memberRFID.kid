<?python
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
     <div  py:def="load_memberRFID(object)" py:strip="True">
           <div py:if="object.rfid" >
               <p>Member Card No.: ${object.rfid} <a href="/rfid/unregister_card" id="removeCard_${object.id}">Remove Card</a></p>
           </div>
           <div py:if="not object.rfid" >
               <p>No Card Issued</p>
           </div>
       </div>
       ${load_memberRFID(object)}
</div>

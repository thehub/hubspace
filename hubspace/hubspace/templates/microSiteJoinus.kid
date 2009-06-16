<?python
submit=None
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>
</head>
<body id="joinus">
    <div class="span-12" id="content-intro">
        <h1 id="title" class="text_small">${page.title and page.title or "Join us"}</h1>
        <div py:if="page.content" class="text_wysiwyg" id="content">${XML(page.content)}</div>
        <div py:if="not page.content" class="text_wysiwyg" id="content">
            <h3>Tariffs*</h3>
            <p><strong>Standard</strong> - 20 hours use of the space per month - &pound;40 p/m (&pound;30)</p>
            <p><strong>Worklite</strong> - 45 hours use of the space per month, registered post box, complimentary tea and coffee - &pound;120 p/m (&pound;100)</p>
            <p><strong>Work +</strong> - 60 hours use of the space, registered post box, complimentary tea and coffee - &pound;170 p/m (&pound;150)</p>
            <p><strong>Unlimited</strong> -  Unlimited hours, registered post box, personal storage, optional phone-line, complimentary tea and coffee - &pound;480 p/m (&pound;400)</p>
            <p>* Prices include VAT, there is no joining fee, prices in grey are available for individuals working for 'start-up' organisations (non-VAT registered)</p>
       </div>
    </div>
    <div class="span-12 last" py:if="submit">
        <div id="membership-enquiry" class="span-12 last content-sub">
            <h3 id="joinus_confirm_header" class="text_small">${page.joinus_confirm_header and page.joinus_confirm_header or "Thank You"}</h3>
            <div py:if="page.joinus_confirm_body" class="text_wysiwyg" id="joinus_confirm_body">${XML(page.joinus_confirm_body)}</div>
            <div py:if="not page.joinus_confirm_body"  id="joinus_confirm_body" class="text_wysiwyg"><p>Thank you for your interest in membership of the Hub Kings Cross. Please download our <a class="pdflink" href="/static/files/Hub_Kings_Cross_Brochure.pdf">brochure</a> for more information on the prices and benefits of membership. One of our hosting team will be in touch shortly to help you answer any queries you may have and to talk you through some of the membership options in more detail. We look forward to you  visiting our space and hope to welcome you as a member of the Hub Kings Cross in the not too distant future.</p>.
            </div>
        </div>
    </div>
    <div class="span-12 last" py:if="not submit">
        <div class="span-12 last content-sub" id="membership-enquiry">
            <h3 id="joinus_enquiry" class="text_small">${page.joinus_enquiry and page.joinus_enquiry or "Membership Enquiry"}</h3>
            <div py:if="page.joinus_enquiry_intro" class="text_wysiwyg_small" id="joinus_enquiry_intro">${XML(page.joinus_enquiry_intro)}</div>
            <div py:if="not page.joinus_enquiry_intro" class="text_wysiwyg_small" id="joinus_enquiry_intro"><p>If you are interested in joining, please fill in this form. You will automatically be emailed a brochure and we will contact you to discuss your needs in more detail.</p></div>
            <form id="enquiry-form" action="./joinConfirm" method="post">
            <fieldset>
                <label for="first_name">First Name</label>
                <input type="text" class="text"  name="first_name" value=""/>
                <label for="last_name">Last Name</label>
                <input type="text" class="text"  name="last_name" value=""/>
                <label for="organisation">Organisation</label>
                <input type="text" class="text"  name="organisation" value=""/>
                <label for="phone">Phone</label>
                <input type="text" class="text"  name="phone" value=""/>
                <label for="email_address">Email</label>
                <input type="text" class="text"  name="email_address" value=""/>
                <input type="submit" value="Submit" class="input-select" />
            </fieldset>
          </form>
        </div>
</div>
</body>
</html>

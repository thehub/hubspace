<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en" xmlns:py="http://purl.org/kid/ns#">
<body>
    <table border="0" align="center" width="100%">
        <?python
            import itertools
            count = itertools.count()
            count.next()

            title_row = invoices_data.pop(0)
        ?>
           <tr class='header'>
                <td>No</td>
                <td>${title_row[0]}</td>
                <td>${title_row[1]}</td>
                <td>${title_row[2]}</td>
                <td>${title_row[3]}</td>
           </tr>
        <div py:for="row in invoices_data">
        <?python
        invoice_id, invoice_number, username, created, amount = row
        ?>
           <tr>
                <td>${count.next()}</td>
                <td><a href="/pdf_invoice/${invoice_id}/${invoice_id}.pdf" target="_blank">${invoice_number}</a></td>
                <td>${username}</td>
                <td>${(created).strftime('%b %d, %Y')}</td>
                <td>${amount}</td>
           </tr>
        </div> 
    </table>
</body>

</html>

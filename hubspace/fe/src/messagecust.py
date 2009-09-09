import pyjd # this is dummy in pyjs.
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.Label import Label
from pyjamas import Window
from pyjamas.ui.TextArea import TextArea
from pyjamas.ui.ListBox import ListBox
from pyjamas.ui.CaptionPanel import CaptionPanel
from pyjamas.ui.FlowPanel import FlowPanel

import remote

location_select_label = "--select--"

def isError(response):
    return "errors" in response

def showCustomizationResult(self, response, request_info):
    print response
    print isError(response)
    if isError(response):
        error_text = response["errors"]["msg_cust"]
        print response["errors"]
        print response["errors"]["msg_cust"]
        print error_text
        self.statusbar.setText(error_text)
    else:
        self.statusbar.setText("Success: Message customized!")
    
def sendForCustomization(self):
    self.statusbar.setText("waiting ..")
    loc_id = self.locations.getValue(self.locations.getSelectedIndex())
    msg_name = self.messages.getValue(self.messages.getSelectedIndex())
    msg_cust = self.messagebox.getText()
    remote.server.customize_message(loc_id, msg_name, msg_cust, self)

class messagecust:

    def onRemoteError(self):
        self.statusbar.setText("Server failed to customize message.")

    def onModuleLoad(self):
        remote.server.get_messagesdata_for_cust(self)

    def onRemoteResponse(self, response, request_info):
        mname = request_info.method
        print response
        if mname == "customize_message":
            showCustomizationResult(self, response, request_info)
            return

        if mname == "get_messagesdata_for_cust":
            locations_data = response["locations"]
            selectionbox = VerticalPanel(Padding=3)
            locations = ListBox()
            for (loc_name, loc_id) in locations_data:
                locations.addItem(loc_id, loc_name)
            messages = ListBox()
            messages.setName("locations")
            messages.addItem(location_select_label)
            for (name, d) in response["messages"].items():
                messages.addItem(d['label'], name)

            locations.addChangeListener(self)
            messages.addChangeListener(self)
            self.locations = locations
            self.messages = messages

            locationbox = HorizontalPanel()
            locationbox.add(Label("Location: ", StyleName="text", Width=80))
            locationbox.add(locations)

            msgnamebox = HorizontalPanel()
            msgnamebox.add(Label("Message: ", StyleName="text", Width=80))
            msgnamebox.add(messages)

            selectionbox.add(locationbox)
            selectionbox.add(msgnamebox)

            mainpanel = VerticalPanel(StyleName="dataBoxContent")
            mainpanel.add(selectionbox)
            self.mainpanel = mainpanel
            root = RootPanel()
            root.add(mainpanel)

        if mname == "get_messagecustdata":
            self.messages_data = response
            buttonspanel = FlowPanel(Spacing=1, Padding=1, Width=600)
            #buttonspanel.add(Label("Macros:", StyleName="text"))
            for macro_d in self.messages_data['macros']:
                macrobutton = Button(macro_d['label'], self, StyleName="buttonlikelink")#"nicebutton small")
                macrobutton.name = macro_d['name']
                buttonspanel.add(macrobutton)

            msgpanel = VerticalPanel(Padding=2, Spacing=2)
            messagebox = TextArea()
            messagebox.setCharacterWidth(80)
            height = len(self.messages_data["text"].split('\n')) + 3
            messagebox.setVisibleLines(height)
            messagebox.setText(self.messages_data["text"])
            messagebox.setName("textBoxFormElement")
            self.messagebox = messagebox
            msgpanel.add(messagebox)
            self.statusbar = Label(StyleName="errorMessage")
            msgpanel.add(self.statusbar)
            actionbuttons = HorizontalPanel(Spacing=2)
            updatebutton = Button("Update", self, StyleName="nicebutton small yellow")
            updatebutton.name = "update"
            actionbuttons.add(updatebutton)
            #actionbuttons.add(Button("Send me a preview mail"))
            msgpanel.add(actionbuttons)

            editorbox = VerticalPanel(Padding=1)
            editorbox.add(buttonspanel)
            editorbox.add(msgpanel)
            editorpanel = CaptionPanel("Message editor", editorbox, Padding=1, StyleName=text)
            editorpanel.name = "editorpanel"
            self.editorpanel = editorpanel

            self.mainpanel.add(editorpanel)

    def onClick(self, sender):
        if sender.name == "update":
            sendForCustomization(self)
        else:
            current_pos = self.messagebox.getCursorPos()
            text1 = self.messagebox.getText()[:current_pos]
            text2 = self.messagebox.getText()[current_pos:]
            text = "%s${%s}%s" % (text1, sender.name, text2)
            self.messagebox.setText(text)

    def onChange(self, sender):
        msg_selection = self.messages.getValue(self.messages.getSelectedIndex())
        loc_id = self.locations.getValue(self.locations.getSelectedIndex())

        if msg_selection == location_select_label: return # ignore
        
        for c in self.mainpanel.getChildren():
            if c.name == "editorpanel":
                self.mainpanel.remove(c)
                break

        remote.server.get_messagecustdata(msg_selection, loc_id, self)

        #if msg_selection not in self.messages_data:
        #    return


if __name__ == '__main__':
    pyjd.setup("http://127.0.0.1/examples/jsonrpc/public/JSONRPCExample.html")
    app = messagecust()
    app.onModuleLoad()
    pyjd.run()



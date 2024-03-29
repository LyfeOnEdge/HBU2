from .detailpage import detailPage
from widgets import button, ThemedLabel
import style
from appstore import getScreenImage
from modules.locations import notfoundimage
import os, sys

class injectorPage(detailPage):
	def __init__(self, parent, controller):
		self.local_packages_handler = controller.local_packages_handler
		self.injector = controller.injector
				
		self.column_inject_button = None		
		detailPage.__init__(self,parent,controller)
		self.column_package.place_forget()

		self.column_installed_version = ThemedLabel(self.column_body,"",anchor="w",label_font=style.smalltext, foreground = style.w, background = style.color_1)
		self.column_installed_version.place(x = 5, width = - 5, y = 3.666 * style.detailspagemultiplier, relwidth = 1, height = 0.333 * style.detailspagemultiplier)

		self.releases_listbox.place(relwidth = 1, y=4.00*style.detailspagemultiplier, relheight = 1, height = - (4*style.detailspagemultiplier + 3 * (style.buttonsize + style.offset) + style.offset))

	def update_page(self,repo):
		self.selected_version = None
		self.repo = repo

		try:
			package = repo["store_equivalent"]
		except:
			package = repo["software"]

		github_content = repo["github_content"]

		version = github_content[0]["tag_name"]

		self.column_title.set("Title: {}".format(repo["name"]))

		self.column_author.set("Author: {}".format(repo["author"]))
		self.column_version.set("Latest Version: {}".format(github_content[0]["tag_name"]))
		try:
			self.column_license.set("License: {}".format(repo["license"]))
		except:
			self.column_license.set("License: N/A")

		installed = self.local_packages_handler.get_package_version(self.repo["store_equivalent"])
		if installed:
			self.column_installed_version.set("Downloaded: {}".format(installed))
		else:
			self.column_installed_version.set("Not downloaded")



		self.column_package.set("Package: {}".format(package))
		self.column_downloads.set("Downloads: {}".format(repo["downloads"]))
		self.column_updated.set("Updated: {}".format(github_content[0]["created_at"]))

		self.content_frame_details.configure(state="normal")
		self.content_frame_details.delete('1.0', "end")

		#Makes newlines in details print correctly. Hacky but :shrug:
		details = repo["description"].replace("\\n", """
"""
			)
		self.content_frame_details.insert("1.0", details)
		self.content_frame_details.configure(state="disabled")


		self.header_label.set(repo["name"])
		self.header_author.set(repo["author"])

		if not self.column_inject_button:
			self.column_inject_button = button(self.column_body, 
				callback = self.trigger_inject, 
				text_string = "INJECT", 
				font=style.mediumboldtext, 
				background=style.color_2
			)

		#Hides or places the uninstalll button if not installed or installed respectively
		#get_package_entry returns none if no package is found or if the sd path is not set
		if self.local_packages_handler.get_package_entry(package):
			self.column_inject_button.place(rely=1,relx=0.5,x = - 1.5 * (style.buttonsize), y = - 1 * (style.buttonsize + style.offset), width = 3 * style.buttonsize, height = style.buttonsize)
			self.column_install_button.settext("CHANGE")
		else:
			self.column_inject_button.place_forget()
			if self.column_install_button:
				self.column_install_button.settext("Download")

		def do_update_banner():
			self.bannerimage = getScreenImage(package)
			if self.bannerimage:
				self.update_banner(self.bannerimage)
			else:
				self.update_banner(notfoundimage)
				print("failed to download screenshot for {}".format(package))

		self.update_releases_listbox()
			
		self.controller.async_threader.do_async(do_update_banner)

	def select_version(self, event):
		try:
			widget = event.widget
			selection=widget.curselection()
			picked = widget.get(selection[0])
			self.selected_version = picked
			self.version_index = self.controller.local_packages_handler.get_tag_index(self.repo["github_content"], self.selected_version)
			self.update_release_notes()
		except Exception as e:
			print(e)

	def trigger_install(self):
		self.controller.async_threader.do_async(self.local_packages_handler.install_package, [self.repo, self.version_index, self.progress_bar.update, self.reload_function, self.progress_bar.set_title], priority = "high")

	def trigger_inject(self):
		toolsfolder = os.path.join(sys.path[0],"tools")
		payloadfolder = os.path.join(toolsfolder, self.repo["install_subfolder"])
		print(self.repo["payload"])
		payload = None
		for item in os.listdir(payloadfolder):
			if os.path.isfile(os.path.join(payloadfolder, item)):
				if item.startswith(self.repo["payload"][0]):
					if item.endswith(self.repo["payload"][1]):
						payload = os.path.join(payloadfolder, item)
						break
		if payload:
			print("injecting {}".format(payload))
			self.injector.inject(payload)
		else:
			print("Failed to find payload")
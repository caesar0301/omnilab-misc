__author__ = "chenxm"

import zlib

from PyOmniMisc.traffic.http import HTTPLogEntry
from PyOmniMisc.utils.web import URL

from PyOmniMisc.model.webtree import WebNode, WebTree


def str_crc32(string):
	return zlib.crc32(string) & 0xffffffff


class User(object):

	def __init__(self, id):
		self.id = id
		self.webtrees = []

	def add_entry(self, http_log_entry):
		""" add one HTTP log entry to this user
		It is skipped if the request time is null.
		Otherwise, we add it to it web tree or create a new tree for it.
		"""
		# create a new node
		nn = WebNode(http_log_entry)
		nn_ref = nn.pl.referer()
		nn_st = nn.pl.rqtstart()
		# it's not a valid HTTP request, return directly
		if nn_st == None:
			return False
		nn_et = nn.pl.rspend()
		nn_md = nn.pl.method()
		nn_ct = nn.pl.type()
		nn_url = nn.pl.url()
		nn_ua = nn.pl.ua()
		# Set readable node tag		
		ntag = "%s | %s | %s | %s | %s | %s |%s " % (
			nn_st, nn_et,
			str(nn_md), str(nn_url)[:50], 
			str(nn_ct).split(";")[0], 
			"Yes" if nn_ref != None else "No", nn_ua)
		nn.tag = ntag # formated tag to show by tree

		# add this node to a web tree of this user
		linked_flag = False
		for webtree in self.webtrees[::-1]:
			last_action_time = webtree.get_nodes()[-1].pl.rqtstart()
			# session idle time equals to 15 mins
			if float(nn_st) - float(last_action_time) <= 60*15: # seconds
				# Find its predecessor
				pred_id = None
				if nn_ref ==  None: break
				nn_ref = URL.strip_proto(nn_ref)
				# create map between URL and node id
				url_nid_map = {}
				for node in webtree.get_nodes():
					node_url = node.pl.url()
					if node_url == None: continue
					node_url = URL.strip_proto(node_url)
					url_nid_map[node_url] = node.identifier
				# find predecessor id
				if nn_ref in url_nid_map: pred_id = url_nid_map[nn_ref]
				if pred_id != None:
					# Predecessor found...
					webtree.add_node(nn, pred_id)
					linked_flag = True
					break

		# After all the trees are checked:	
		if not linked_flag:
			new_tree = WebTree()
			if nn_ref != None:
				dn = WebNode(HTTPLogEntry())
				dn.type = 0	# dummy signature
				dn.pl['request_timestamp'] = nn.pl.rqtstart()
				nn_ref = URL.strip_proto(nn_ref)
				chops = nn_ref.split('/', 1)
				dn.pl['request_host'] = chops[0]
				if len(chops) == 1:
					dn.pl['request_url'] = ''
				else:
					dn.pl['request_url'] = '/' + chops[1]
				dn.tag = "(dummy) %s | %s" % (dn.pl.rqtstart(), dn.pl.url()[:50])
				new_tree.add_node(dn, parent=None)
				new_tree.add_node(nn, dn.identifier)
			else:
				new_tree.add_node(nn, parent=None)
			self.webtrees.append(new_tree)
			return True
			
			
	def is_mobile(self):
		'''
		Check if the user is mobile
		If half of the occured user agents are detected as mobile, 
		we mark him/her as the mobile
		'''
		ua_set = set()
		for webtree in self.webtrees:
			for nid in webtree.expand_tree():
				ua = webtree[nid].get("request_user_agent")
				if ua: ua_set.add(ua)
		return False


	def pretty_print(self, filename=None, show=True):
		'''
		Print and output web trees of this user.
		'''
		# print prefix of user ID
		if filename:
			open(filename,'ab').write("*****[[ %s ]]******\n" % self.id)
		# sort all web trees
		self.webtrees.sort(key=lambda x: x[x.root].pl.rqtstart())
		# traverse all trees of this user
		for tree in self.webtrees:
			if tree is None:
				continue
			if filename:
				tree.save2file(filename)
			if show:
				tree.show(key=lambda x: x.pl.rqtstart(), reverse=False)
		

if __name__ == '__main__':
	user = User(1)
	print user.is_mobile()
	user.pretty_print()
	print str_crc32("helloworld") #4192936109
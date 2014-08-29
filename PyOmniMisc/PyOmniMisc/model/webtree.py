__author__ = 'chenxm'

from treelib import Tree, Node
from PyOmniMisc.traffic.http import HTTPLogEntry
from PyOmniMisc.utils.web import URL


class WebNode(Node):

	def __init__(self, http_entry):
		assert isinstance(http_entry, HTTPLogEntry)
		Node.__init__(self)
		self._dummy = 0	# help to process dummy nodes
		self.aem_pred = None # the classified type for preceeding entity by AEM model
		self.aem_last = None # the classified type for LAST entity by AEM model
		self.fake_link = True # if the link is fake derived from referrer
		self.pl = http_entry # http log entries
		self.tag = self.gen_tag() # formated tag to show by tree

	def gen_tag(self):
		# Set readable node tag		
		ntag = "%s (%s/%s) | %s | %s | %s | %s | %s | %s" % (
			self.pl.rqtstart(),
			self.aem_pred,
			self.aem_last,
			self.pl.rspend(),
			str(self.pl.method()),
			str(self.pl.url())[:80], 
			str(self.pl.type()).split(";")[0], 
			"Ref" if self.pl.referer() != None else "NoRef",
			str(self.pl.ua())[-30:])
		return ntag


class WebTree(Tree):

	def __init__(self, tree=None):
		Tree.__init__(self, tree)


	def sorted_nodes(self):
		""" get a list of nodes ordered by request time
		"""
		nodes = self.all_nodes()
		if len(nodes) > 0:
			assert isinstance(nodes[0], WebNode)
			nodes.sort(key=lambda x: x.pl.rqtstart())
		return nodes

	def duration(self):
		''' duration for this tree
		'''
		nodes = self.sorted_nodes()
		starts = [n.pl.rqtstart()for n in nodes if n.pl.rqtstart() != None ]
		ends = [n.pl.rspend() for n in nodes if n.pl.rspend() != None ]
		start = None if len(starts) == 0 else min(starts)
		end = None if len(ends) == 0 else max(ends)
		return (start, end)

	@staticmethod
	def plant(http_entries):
		'''
		Generate trees from a batch of http_entries: a classic method
		'''
		if len(http_entries) > 0:
			assert isinstance(http_entries[0], HTTPLogEntry)
		# create a tree list
		wts = []
		for e in http_entries:
			# create a new node
			nn = WebNode(e)
			nn_ref = nn.pl.referer()
			nn_st = nn.pl.rqtstart()
			if nn_st == None: # it's not a valid HTTP request
				continue

			# add this node to a web tree of this user
			linked_flag = False
			for wt in wts[::-1]:
				lat = wt.sorted_nodes()[-1].pl.rqtstart()
				# session idle time equals to 15 mins
				if float(nn_st) - float(lat) <= 60*15: # seconds
					# Find its predecessor
					pred_id = None
					if nn_ref ==  None:
						break
					#nn_ref = URL.strip_proto(URL.strip_param(nn_ref)) # strip proto and params
					nn_ref = URL.strip_proto(nn_ref)
					# create map between URL and node id
					un_map = {}
					for node in wt.sorted_nodes():
						url = node.pl.url()
						if url == None:
							continue
						#url = URL.strip_proto(URL.strip_param(url)) # strip proto and params
						url = URL.strip_proto(url)
						un_map[url] = node.identifier
					# find predecessor id
					if nn_ref in un_map:
						pred_id = un_map[nn_ref]
					if pred_id != None:
						# Predecessor found...
						wt.add_node(nn, pred_id)
						linked_flag = True
						break

			# After all the trees are checked:	
			if not linked_flag:
				nt = WebTree()
				if nn_ref != None:
					dn = WebNode(HTTPLogEntry())
					dn._dummy = 0	# dummy flag
					dn.pl['request_timestamp'] = nn.pl.rqtstart()
					nn_ref = URL.strip_proto(nn_ref)
					chops = nn_ref.split('/', 1)
					dn.pl['request_host'] = chops[0]
					if len(chops) == 1:
						dn.pl['request_url'] = ''
					else:
						dn.pl['request_url'] = '/' + chops[1]
					dn.tag = "(dummy) %s | %s" % (dn.pl.rqtstart(), dn.pl.url()[:50])
					nt.add_node(dn, parent=None)
					nt.add_node(nn, dn.identifier)
				else:
					nt.add_node(nn, parent=None)
				wts.append(nt)
		return wts


	def start_time(self):
		""" Get the start time of the first entry
		"""
		sn = self.sorted_nodes()
		if len(sn) > 0:
			return sn[0].pl.rqtstart()
		return None


	def fruits(self):
		""" Return a list of payload carried by the node 
		"""
		f = []
		for node in self.all_nodes():
			f.append(node.pl)
		return f
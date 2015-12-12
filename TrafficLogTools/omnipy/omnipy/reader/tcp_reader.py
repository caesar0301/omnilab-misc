import csv

from ._reader import LogEntry, LogReader

__author__ = 'chenxm'
__all__ = ["TCPLogReader", "TCPLogEntry"]


_TCP_STATISTICS = [
	"source_ip_addr",
	"source_tcp_port",
	"source_packets",
	"source_rst_sent",
	"source_ack_sent",
	"source_pure_ack_sent",
	"source_unique_bytes",
	"source_data_packets",
	"source_data_bytes",
	"source_rexmit_packets",
	"source_rexmit_bytes",
	"source_out_sequence_packets",
	"source_syn_count",
	"source_fin_count",
	"source_rfc1323_ws_sent",
	"source_rfc1323_ts_sent",
	"source_window_sacle_factor",
	"source_sack_option_set",
	"source_sack_sent",
	"source_mss_declared",
	"source_max_segment_size_observed",
	"source_min_segment_size_observed",
	"source_max_receiver_windows_announced",
	"source_min_receiver_windows_announced",
	"source_segements_window_zero",
	"source_max_cwin__in_flight_size_",
	"source_min_cwin__in_flight_size_",
	"source_initial_cwin__in_flight_size_",
	"source_average_rtt",
	"source_min_rtt",
	"source_max_rtt",
	"source_standard_deviation_rtt",
	"source_valid_rtt_count",
	"source_min_ttl",
	"source_max_ttl",
	"source_rexmit_segments_rto",
	"source_rexmit_segments_rto",
	"source_packet_recording_observed",
	"source_network_duplicated_observed",
	"source_unknown_segments_classified",
	"source_rexmit_segments_flow_control",
	"source_unnece_rexmit_rto",
	"source_unnece_rexmit_fr",
	"source_rexmit_syn_different_initial_seqno",
	"dest_ip_addr",
	"dest_tcp_port",
	"dest_packets",
	"dest_rst_sent",
	"dest_ack_sent",
	"dest_pure_ack_sent",
	"dest_unique_bytes",
	"dest_data_packets",
	"dest_data_bytes",
	"dest_rexmit_packets",
	"dest_rexmit_bytes",
	"dest_out_sequence_packets",
	"dest_syn_count",
	"dest_fin_count",
	"dest_rfc_1323_ws_sent",
	"dest_rfc_1323_ts_sent",
	"dest_window_sacle_factor",
	"dest_sack_option_set",
	"dest_sack_sent",
	"dest_mss_declared",
	"dest_max_segment_size_observed",
	"dest_min_segment_size_observed",
	"dest_max_receiver_windows_announced",
	"dest_min_receiver_windows_announced",
	"dest_segements_window_zero",
	"dest_max_cwin__in_flight_size_",
	"dest_min_cwin__in_flight_size_",
	"dest_initial_cwin__in_flight_size_",
	"dest_average_rtt",
	"dest_min_rtt",
	"dest_max_rtt",
	"dest_standard_deviation_rtt",
	"dest_valid_rtt_count",
	"dest_min_ttl",
	"dest_max_ttl",
	"dest_rexmit_segments_rto",
	"dest_rexmit_segments_fr",
	"dest_packet_recording_observed",
	"dest_network_duplicated_observed",
	"dest_unknown_segments_classified",
	"dest_rexmit_segments_flow_control",
	"dest_unnece_rexmit_rto",
	"dest_unnece_rexmit_fr",
	"dest_rexmit_syn_different_initial_seqno",
	"flow_duration",
	"flow_first_packet_time_offset",
	"flow_last_segment_time_offset",
	"source_first_payload_time_offset",
	"dest_first_payload_time_offset",
	"source_last_payload_time_offset",
	"dest_last_payload_time_offset",
	"source_first_pure_ack_time_offset",
	"dest_first_pure_ack_time_offset",
	"flow_first_packet_absolute_time",
	"source_has_internal_ip",
	"dest_has_internal_ip",
	"flow_type_bitmask",
	"flow_p2p_type",
	"flow_p2p_subtype",
	"p2p_ed2k_data_message_number",
	"p2p_ed2k_signaling_message_number",
	"p2p_ed2k_c2s_message_number",
	"p2p_ed2k_s2c_message_number",
	"p2p_ed2k_chat_message_number",
	"flow_http_type",
	"flow_ssl_source_hello",
	"flow_ssl_dest_hello",
]


class TCPLogEntry(LogEntry):

	def __init__(self):
		LogEntry.__init__(self)
		for key in _TCP_STATISTICS:
			self[key] = None

	@staticmethod
	def all():
		""" Get all properties of TCP log entry
		"""
		return _TCP_STATISTICS

	def socket(self):
		""" Get the socket of this entry
		"""
		for item in ['source_ip_addr', 'source_tcp_port', 'dest_ip_addr', 'dest_tcp_port']:
			if self[item] is None:
				assert("Invalid TCP log entry: %s can't be None" % item)
		source = (self['source_ip_addr'], self['source_tcp_port'])
		dest = (self['dest_ip_addr'], self['dest_tcp_port'])
		return (source, dest)


class TCPLogReader(LogReader):

	def __init__(self, tcp_log_name, quiet = True):
		LogReader.__init__(self, tcp_log_name)
		self._csv_reader = csv.reader(self.filehandler, delimiter = ' ')
		self._quiet = quiet

	def next(self):
		tcp_log_entry = None
		segments = []
		try:
			segments = self._csv_reader.next()
		except StopIteration:
			self.filehandler.close()
			raise StopIteration
		except csv.Error as e:
			if not self._quiet:
				print('WARNNING: file %s, line %d: %s' % (self.filename, self._csv_reader.line_num, e))

		if len(segments) == len(_TCP_STATISTICS):
			tcp_log_entry = TCPLogEntry()
			for i in range(0, len(_TCP_STATISTICS)):
				value = segments[i]
				tcp_log_entry[_TCP_STATISTICS[i]] = value

		return tcp_log_entry
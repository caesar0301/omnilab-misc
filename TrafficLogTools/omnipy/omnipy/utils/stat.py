import math


__author__ = 'chenxm'
__all__ = ["FMeasure", "FMeasureBeta", "MSE", "RMSE"]


def FMeasure(precision, recall):
	""" Also known as F-one measure
	"""
	return FMeasureBeta(precision, recall, 1)

def FMeasureBeta(precision, recall, beta):
	""" The F-measure was derived by van Rijsbergen (1979) so that F_beta
	'measures the effectiveness of retrieval with respect to a user who 
	attaches beta times as much importance to recall as precision'.
	"""
	return (1.0+math.pow(beta, 2)) * (precision*recall) / (math.pow(beta,2)*precision + recall)

def MSE(predictions, targets):
	""" Mean Square Error
	"""
	if not isinstance(predictions, list) or not isinstance(targets, list) or \
		len(predictions) != len(targets):
		raise ValueError("Invalid parameters: two lists with equal length are required")
	l = len(predictions)
	se = [math.pow(predictions[i]-targets[i], 2) for i in range(l)]
	mse = sum(se)/l
	return mse

def RMSE(predictions, targets):
	""" Root of Mean Square Error
	"""
	return math.sqrt(MSE(predictions, targets))
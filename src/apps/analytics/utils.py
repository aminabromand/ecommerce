

def get_client_ip(request):
	x_forwareded_for = request.META.get('HTTP_X_FORWAREDED_FOR')
	if x_forwareded_for:
		ip = x_forwareded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

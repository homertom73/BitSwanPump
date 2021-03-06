#!/usr/bin/env python3
import sys
import bspump
import bspump.socket
import bspump.common


class SamplePipeline(bspump.Pipeline):

	'''
	To test this pipeline, use:
	socat STDIO TCP:127.0.0.1:8082
	'''

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.socket.TCPSource(app, self, config={'host': '127.0.0.1', 'port': 8082}),
			bspump.common.PPrintSink(app, self, "AMQPConnection1", stream=sys.stderr)
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")
	svc.add_pipeline(SamplePipeline(app, "SamplePipeline"))
	app.run()

import abc

from .processor import ProcessorBase


class Generator(ProcessorBase):
	"""
    Generator object is used to generate one or multiple events in asynchronous way
    and pass them to following processors in the pipeline.
    In the case of Generator, user overrides `generate` method, not `process`.

    1.) Generator can iterate through an event to create derived ones and pass them to following processors.
    Generator can in the same way also generate completely independent events, if necessary.

    Example of a custom Generator class with generate method:

.. code:: python

        class MyGenerator(bspump.Generator):

            async def generate(self, context, event, depth):
                for item in event.items:
                    await self.Pipeline.inject(context, item, depth)

    2.) Generator can be used for OOB-processing. In this way, the generator processes originally
    synchronous events "out-of-band" e.g. out of the synchronous processing within the pipeline.

    Specific implementation of the generator should implement the generate method to process events while performing
    long running (asynchronous) tasks such as HTTP requests.
    The long running tasks may enrich events with relevant information, such as output of external calculations.

    Example of generate method:

.. code:: python

        async def generate(self, context, event):

            async with aiohttp.ClientSession() as session:
                async with session.get("https://example.com/resolve_color/{}".format(event.get("color_id", "unknown"))) as resp:
                    if resp.status != 200:
                        return event
                color = await resp.json()
                event["color"] = color

            await self.Pipeline.inject(context, output_event, depth)
"""

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		# The correct depth is later set by the pipeline
		self.PipelineDepth = None

	def set_depth(self, depth):
		assert(self.PipelineDepth is None)
		self.PipelineDepth = depth

	def process(self, context, event):
		assert(self.PipelineDepth is not None)
		self.Pipeline.ensure_generator_future(
			self.generate(context, event, self.PipelineDepth + 1)
		)
		return None

	@abc.abstractmethod
	async def generate(self, context, event, depth):
		raise NotImplemented()

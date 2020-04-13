from string import ascii_lowercase
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from itertools import cycle

class CalculateFrequency(beam.DoFn):
    def process(self, element, total_characters):
        letter, counts = element
        yield letter, '{:.2%}'.format(counts / float(total_characters))

def run():
    options = PipelineOptions()
    options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=options) as p:
        letters = (p | beam.Create(cycle("XYZ"))
                    | beam.FlatMap(lambda line: (ch for ch in line.lower() if ch
                                                in ascii_lowercase))
                    | beam.Map(lambda x: (x, 1)))

        counts = (letters | beam.CombinePerKey(sum))

        total_characters = (letters | beam.MapTuple(lambda x, y: y)
                                    | beam.CombineGlobally(sum))

        (counts | beam.ParDo(CalculateFrequency(),
                            beam.pvalue.AsSingleton(total_characters))
                | beam.Map(lambda x: print(x)))


if __name__ == '__main__':
    run()
import sys, os, subprocess

class BatchTokenizer(object):
    def __init__(self, language, working_dir, moses_installation_dir):
        # Ensure the perl tokenizer is exists
        self.__tokeniser = os.path.join(moses_installation_dir,
                                        'scripts',
                                        'tokenizer',
                                        'tokenizer.perl')
        if not os.path.exists(self.__tokeniser):
            raise Exception("Perl tokenizer does not exist at [%s]" % self.__tokeniser)

        self.__working_dir = working_dir
        if not os.path.exists(self.__working_dir):
            os.makedirs(self.__working_dir)
        
        self.__language = language

    def tokenise(self, filename):
        basefilename = os.path.basename(filename)
        outfilename = os.path.join(self.__working_dir, basefilename + '.tok')
        cmd = '%s -q -l %s < %s > %s' % (self.__tokeniser, self.__language, filename, outfilename)
        pipe = subprocess.Popen(cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE, shell=True)
        pipe.wait()

        return outfilename


def configure(args):
    return {'language' : args['language'],
            'tokenisation_dir' : args['tokenisation_dir'],
            'moses_installation_dir' : args['moses_installation_dir']}


def initialise(config):
    tokenizer = BatchTokenizer(config['language'],
                               config['tokenisation_dir'],
                               config['moses_installation_dir'])

    def process(a, s):
        tokenised_filename = tokenizer.tokenise(a['filename'])
        return {'tokenised_filename' : tokenised_filename}

    return process


if __name__ == '__main__':
    def __test():
        configuration = {'language' : 'de',
                         'tokenisation_dir' : 'test_data',
                         'moses_installation_dir' : os.path.abspath(os.getenv('MOSES_HOME'))}
        values = {'filename' : os.path.join('test_data', 'test.de')}
        from pypeline.helpers.helpers import run_pipeline, cons_function_component
        box = cons_function_component(initialise(configure(configuration)))
        print run_pipeline(box, values, None)

    # Test!
    __test()

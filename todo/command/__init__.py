"""Interactive shell framework."""

class Command():
    def __init__(self):
        self.commands = dict()
        self.start_up = Command._start_up_stab
        self.clean_up = Command._clean_up_stub
        self.welcome_message = ''
        self.help = 'HELP: command  [options...]         DESCRIPTION\n\n' + \
                    'help                                show this message\n' + \
                    'quit                                quit todo\n'

    @staticmethod
    def _start_up_stab():
        pass

    @staticmethod
    def _clean_up_stub():
        pass

    def set_start_up(self):
        def decorator(func):
            self.start_up = func
            return func
        return decorator

    def set_clean_up(self):
        def decorator(func):
            self.clean_up = func
            return func
        return decorator

    def add_command(self, command, func, **options):
        self.commands[command] = (func, options)
        if 'args' in options:
            self.help += '{:<15}{:<21}'.format(
                command,
                ' '.join('[%s]' % arg for arg in options['args'])
            )
        else:
            self.help += '{:<15}                     '.format(command)
        if 'help' in options:
            self.help += options['help'] + '\n'
        else:
            self.help += '\n'

    def command(self, command, **options):
        """Decorator for implement ToDo commands.
        USAGE:
        app = Command()
        
        @app.command('list')
        def list():
            return todo_list
        app.run()
        """
        def decorator(func):
            self.add_command(command, func, **options)
            return func
        return decorator

    def run(self):
        self.start_up()
        if self.welcome_message:
            print(self.welcome_message)

        while True:
            command, *args = input('> ').split(' ')
            try:
                func, options = self.commands[command]
                if 'args' not in options:
                    result = func()
                elif len(options['args']) <= len(args):
                    # @app.command('command', args=[]) のargsで決めた引数だけ取り込む
                    # もう少し作り込めそうだけどとりあえずこれだけ
                    result = func(*args[:len(options['args'])])
                else:
                    args += [''] * (len(options['args']) - len(args))
                    result = func(*args)
                print(result)
            except KeyError:
                if command == 'quit':
                    break
                if command == 'help':
                    print(self.help) # include command:'help'
                else:
                    print('see: > help')

        self.clean_up()
        print('Bye!')


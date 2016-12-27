import iso.remote.adapter.ftp as ftpadapter

class Filer():
    def __init__(self, adapter_name, *args):
        module_name = adapter_name.lower()
        class_name = adapter_name.upper()
        mod = __import__('iso.remote.adapter.' + module_name, globals(), locals(), [class_name], 0)
        adapter_python_class = getattr(mod, class_name)
        self.adapter = adapter_python_class(*args)

    def get_filename(self, full_version, distribution):
        return self.adapter.get_filename(full_version, distribution)

    def get_files(self):
        return self.adapter.get_files()

    def get_versions(self, entry_list):
        return self.adapter.get_versions(entry_list)

    def iso_exists(self, full_version, distribution):
        return self.adapter.iso_exists(full_version, distribution)

    def download_on(self, check_function, check_versions, distribution):
        self.adapter.download_on(check_function, check_versions, distribution)

    def generate(self, check_versions, virt_types, distribution):
        self.adapter.generate(check_versions, virt_types, distribution)

    def set_releases_location(self, release_folder):
        self.adapter.set_releases_location(release_folder)

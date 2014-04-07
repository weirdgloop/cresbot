
class Page:
    def __init__(self, api, page):
        print('init')
	
    def get_content(self):
        """
        Gets the wikitext of the page
        """
        print('get_content')
    
    def get_images(self):
        """
        Gets a list of images used on the page
        """
        print('get_images')
    
    def get_categories(self):
        """
        Gets a list of categories on the page
        """
        print('get_categories')
    
    def get_templates(self):
        """
        Gets a list of templates on the page
        """
        print('get_templates')
    
    def edit(self):
        """
        Edits the page
        """
        print('edit')
    
    def move(self):
        """
        Moves the page
        """
        print('move')
    
    def protect(self):
        """
        Protects the page
        """
        print('protect')
    
    def delete(self):
        """
        Deletes the page
        """
        print('delete')
    
    def undelete(self):
        """
        Undeletes the page
        """
        print('undelete')
    
    def links_to_page(self):
        """
        Gets pages that link to the current page
        """
        print('links_to_page')
    
    def transcludes_page(self):
        """
        Get pages that transclude the current page
        """
        print('transcludes_page')

#!/usr/bin/env python

from pprint import pprint
from mendeley_client import *
import os
import sys


class MendeleyOapi(object):
    def __init__(self, config):
        print "====================="
	self.config = config
        self.mendeley = create_client(config)

    def getVerificationUrl(self):
        self.mendeley = MendeleyClient(self.config.api_key, self.config.api_secret)
	print "URL:",self.mendeley.interactive_auth_url()

    def setVerificationCode(self, code):
        print "Code", code 
        # self.mendeley.set_access_token(code)
        self.mendeley.interactive_set_access_token(code)

    def isValid(self):
        return self.mendeley != None

    def getFolderId(self,folders, name):
        for folder in folders:
            if folder['name'] == name:
	        return folder['id']
    
        return None
    
    def authorsToString(self,authors):
        a = ''
    
        for author in authors:
            a += author['surname'] + ', ' + author['forename']
    
        return a
    
    def downloadFile(self,document):
        if document.has_key('files'):
            file_hash = document['files'][0]['file_hash']
	    document_id = document['id']
    
            path = '/tmp/' + file_hash + '.pdf'
            file_content = self.mendeley.download_file(document_id, file_hash)
	    f=open(path, 'w')
	    f.write(str(file_content))
	    f.close()
    
	    return path
    
        return ''
    
    def getDocumentMetaInformation(self,document_id):
        document = self.mendeley.document_details(document_id)
        d = {}
        d['title'] = document['title']
        d['authors'] = self.authorsToString(document['authors'])
        d['path'] = self.downloadFile(document)
        return d
    
    def getDocumentsMetaInformation(self,documents):
        documents_information = []
        for document in documents['documents']:
	    documents_information.append(self.getDocumentMetaInformation(document['id']))
    
        return documents_information
    
    def get_mendeley_documents(self):
        folders = self.mendeley.folders()
    
        folderId = self.getFolderId(folders, 'calibre')
    
        documents = self.mendeley.folder_documents(folderId)
        documents_information = self.getDocumentsMetaInformation(documents)
    
        return documents_information

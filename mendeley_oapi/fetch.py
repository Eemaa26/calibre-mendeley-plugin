#!/usr/bin/env python

from pprint import pprint
from mendeley_client import *
import tempfile
import os
import sys

class OapiConfig:
    def __init__(self):
        setattr(self,'api_key', 'c168ce62964a4900e66d9361bda9cb3a04cf98732')
        setattr(self,'api_secret', '7d4294168e43807651faf051510c707b')
        setattr(self,'host', 'api.mendeley.com')

class calibreMendeleyOapi(object):
    def __init__(self, config, tokens_store, calibreAbort = None, calibreLog = None, calibreNotifications = None):
        self.config = config
        self.mendeley = create_client(config,tokens_store)
        self.calibreAbort = calibreAbort
        self.calibreLog = calibreLog
        self.calibreNotifications = calibreNotifications
        self.non_documents_steps = 1

    def getVerificationUrl(self):
        self.mendeley = MendeleyClient(self.config.api_key, self.config.api_secret)
        return self.mendeley.interactive_auth_url()

    def setVerificationCode(self, code):
        self.mendeley.interactive_set_access_token(code)

    def isValid(self):
        return self.mendeley != None

    def getFolderId(self,folders, name):
        for folder in folders:
            if folder['name'] == name:
                return folder['id']

        return None

    def authorsToCalibre(self,authors):
        a = []

        for author in authors:
            a.append(author['forename'] + ' ' + author['surname'])

        return a

    def downloadFile(self,document):
        if document.has_key('files'):
            file_hash = document['files'][0]['file_hash']
            document_id = document['id']

            f=tempfile.NamedTemporaryFile(suffix='.pdf',delete=False)
            path = f.name
            file_content = self.mendeley.download_file(document_id, file_hash)
            f.write(file_content['data'])
            f.close()

            return path

        return ''

    def getDocumentMetaInformation(self,document_id):
        document = self.mendeley.document_details(document_id)
        d = {}
        d['title'] = document['title']
        d['authors'] = self.authorsToCalibre(document['authors'])
        d['path'] = self.downloadFile(document)
        d['mendeley_id'] = document['id']
        return d

    def getDocumentsMetaInformation(self,documents):
        documents_information = []

        total_documents = documents['total_results']
        count = 0

        notification_message = 'Fetching documents'
        self.calibreNotifications.put((1.0/(total_documents+1), notification_message))

        for document in documents['documents']:
            count += 1
            if self.calibreAbort.is_set():
                break

            documents_information.append(self.getDocumentMetaInformation(document['id']))

            progress_number = float(count)/(total_documents + self.non_documents_steps)
            message = "%s, %d of %d" % (notification_message, count, total_documents)

            self.calibreNotifications.put((progress_number, message))

        return documents_information

    def get_mendeley_documents(self):
        self.calibreNotifications.put((0.0, 'Fetching initial information'))
        folders = self.mendeley.folders()

        folderId = self.getFolderId(folders, 'calibre')
        if folderId == None:
            return []

        documents = self.mendeley.folder_documents(folderId)
        documents_information = self.getDocumentsMetaInformation(documents)

        return documents_information

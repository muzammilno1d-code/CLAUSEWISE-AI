
import unittest

from app.services.document_classifier import classify_document


class TestDocumentClassifier(unittest.TestCase):

    def test_employment_agreement(self):
        text = """
        EMPLOYMENT AGREEMENT
        This agreement is between the employer and employee.
        The employee shall receive an annual salary.
        The notice period and probation period shall apply.
        """

        result = classify_document(text)

        self.assertEqual(result["document_type"], "Employment Agreement")
        self.assertEqual(result["status"], "CLASSIFIED")

    def test_rental_agreement(self):
        text = """
        RENTAL AGREEMENT
        The landlord agrees to rent the property to the tenant.
        The tenant shall pay monthly rent and a security deposit.
        """

        result = classify_document(text)

        self.assertEqual(result["document_type"], "Rental / Lease Agreement")
        self.assertEqual(result["status"], "CLASSIFIED")

    def test_service_agreement(self):
        text = """
        SERVICE AGREEMENT
        The service provider agrees to provide services to the client.
        The scope of services and service fees are described below.
        """

        result = classify_document(text)

        self.assertEqual(result["document_type"], "Service Agreement")
        self.assertEqual(result["status"], "CLASSIFIED")

    def test_business_agreement(self):
        text = """
        PARTNERSHIP AGREEMENT
        The business partners agree to share profits.
        Capital contribution and business operations are defined.
        """

        result = classify_document(text)

        self.assertEqual(result["document_type"], "Business Agreement")
        self.assertEqual(result["status"], "CLASSIFIED")

    def test_nda(self):
        text = """
        NON-DISCLOSURE AGREEMENT
        The receiving party shall protect confidential information.
        The disclosing party may share trade secrets.
        """

        result = classify_document(text)

        self.assertEqual(result["document_type"], "Non-Disclosure Agreement")
        self.assertEqual(result["status"], "CLASSIFIED")

    def test_property_sale_deed(self):
        text = """
        REGISTERED SALE DEED

        The purchaser agrees to purchase the property
        from the vendor for the stated consideration amount.

        Survey Number 123.
        Schedule of Property.
        Property Boundaries.
        Sub Registrar.
        """

        result = classify_document(text)

        self.assertEqual(result["document_type"], "Property Sale Deed")
        self.assertEqual(result["document_type_code"], "PROPERTY_SALE_DEED")
        self.assertEqual(result["status"], "CLASSIFIED")

    def test_property_sale_agreement(self):
        text = """
        SALE AGREEMENT

        This agreement is made between the proposed seller
        and proposed purchaser.

        Advance Payment: 100000.
        Balance Consideration: 500000.
        Property Schedule.
        Agreement Date: 05-05-2019.
        """

        result = classify_document(text)

        self.assertEqual(
            result["document_type"],
            "Property Sale Agreement"
        )
        self.assertEqual(
            result["document_type_code"],
            "PROPERTY_SALE_AGREEMENT"
        )
        self.assertEqual(result["status"], "CLASSIFIED")

    def test_encumbrance_certificate(self):
        text = """
        ENCUMBRANCE CERTIFICATE

        Registration Year 2024.
        Survey Number 123.
        Transaction Details.
        Period of Search.
        Sub Registrar Office.
        """

        result = classify_document(text)

        self.assertEqual(
            result["document_type"],
            "Encumbrance Certificate"
        )
        self.assertEqual(
            result["document_type_code"],
            "ENCUMBRANCE_CERTIFICATE"
        )
        self.assertEqual(result["status"], "CLASSIFIED")

    def test_ec_application_or_certified_copy(self):
        text = """
        APPLICATION FOR ENCUMBRANCE CERTIFICATE

        Applicant Name: Sample Applicant.
        Application Number: 12345.
        Period of Search: 01-01-2000 to 31-12-2020.
        Certified Copy.
        Fee Paid.
        """

        result = classify_document(text)

        self.assertEqual(
            result["document_type"],
            "Encumbrance Certificate Application / Copy"
        )
        self.assertEqual(
            result["document_type_code"],
            "EC_APPLICATION_OR_COPY"
        )
        self.assertEqual(result["status"], "CLASSIFIED")

    def test_unknown_document(self):
        text = """
        This document contains general information about
        computer programming and software development.
        """

        result = classify_document(text)

        self.assertEqual(result["document_type"], "Unknown")
        self.assertEqual(result["status"], "UNCLASSIFIED")

    def test_empty_document(self):
        result = classify_document("")

        self.assertEqual(result["document_type"], "Unknown")
        self.assertEqual(result["status"], "INSUFFICIENT_TEXT")

    def test_ambiguous_document(self):
        text = """
        EMPLOYMENT AGREEMENT AND SERVICE AGREEMENT

        The employer and employee agree to a service agreement.
        The service provider shall provide services to the client.
        The employee shall receive an annual salary.
        The scope of services and notice period are also defined.
        """

        result = classify_document(text)

        self.assertEqual(result["document_type"], "Unknown")
        self.assertEqual(result["status"], "AMBIGUOUS")


if __name__ == "__main__":
    unittest.main()

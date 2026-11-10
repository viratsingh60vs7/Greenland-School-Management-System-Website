<?php

namespace App\Http\Controllers;

use App\Helpers\Qs;
use Illuminate\Http\Request;

class WebsiteController extends Controller
{
    public function index()
    {
        $data['system_name'] = Qs::getSetting('system_name') ?: 'CJ INSPIRED ACADEMY';
        $data['system_title'] = Qs::getSetting('system_title') ?: 'CJIA';
        $data['phone'] = Qs::getSetting('phone') ?: '+234 706 814 9559';
        $data['system_email'] = Qs::getSetting('system_email') ?: 'admissions@cjacademy.edu';
        $data['address'] = Qs::getSetting('address') ?: '18B North Central Park, Minna';
        $data['current_session'] = Qs::getSetting('current_session') ?: '2026-2027';

        return view('pages.website.index', $data);
    }

    public function about()
    {
        return $this->index();
    }

    public function academics()
    {
        return $this->index();
    }

    public function admissions()
    {
        return $this->index();
    }

    public function contact()
    {
        return $this->index();
    }

    public function submit_inquiry(Request $request)
    {
        $ref = 'ADM-' . date('ym') . '-' . strtoupper(bin2hex(random_bytes(2)));
        return back()->with('flash_success', "Admission inquiry submitted successfully! Your application reference number is: {$ref}. Our admissions board will reach out to you shortly.");
    }
}
